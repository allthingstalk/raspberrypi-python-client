# -*- coding: utf-8 -*-

#for documentation about the mqtt lib, check https://pypi.python.org/pypi/paho-mqtt/0.9
import paho.mqtt.client as mqtt                # provides publish-subscribe messaging support
import os                                      # so we can get the OS type
import calendar                                # for getting the epoch time
import time                                    # gets the current time
import httplib                                 # for http comm

#get the mac address from this computer
def getMac():
    if os.name == 'nt':
        from netbios import *
        # code ported from "HOWTO: Get the MAC Address for an Ethernet Adapter"
        # MS KB ID: Q118623
        ncb = NCB()
        ncb.Command = NCBENUM
        la_enum = LANA_ENUM()
        ncb.Buffer = la_enum
        rc = Netbios(ncb)
        if rc != 0:
            raise RuntimeError("Unexpected result %d" % (rc,))
        i = 0
        ncb.Reset()
        ncb.Command = NCBRESET
        ncb.Lana_num = ord(la_enum.lana[i])
        rc = Netbios(ncb)
        if rc != 0:
            raise RuntimeError("Unexpected result %d" % (rc,))
        ncb.Reset()
        ncb.Command = NCBASTAT
        ncb.Lana_num = ord(la_enum.lana[i])
        ncb.Callname = "*               "
        adapter = ADAPTER_STATUS()
        ncb.Buffer = adapter
        Netbios(ncb)
        mac = ""
        for ch in adapter.adapter_address:
            mac += "%02x:" % (ord(ch),),
        return mac;
    elif os.name == 'posix':
        import socket
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

#store the mac address so we only need to calculate it 1 time.
mac = getMac();

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    msg = "Connected to mqtt with result code "+str(rc)
    print(msg)
    if DeviceId is None:
        print("device id not specified")
        raise Exception("DeviceId not specified")
    topic = "/m/" + DeviceId + "/#"
    client.subscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    topic = "s" + topic[1:]
    client.subscribe(topic)
    print("subscribed to topics, receiving data from the cloud")

# The callback for when a PUBLISH message is received from the server.
def on_MQTTmessage(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if on_message is not None:
        on_message(msg.topicParts[-1], msg.payload)


#private reference to the mqtt client object for which we reserve a mem loc from the start
_mqttClient = None
_httpServerName = None
_httpClient = None

#public
#######

#has to be provided by the module consumer:

#callback for receiving values from the IOT platform
on_message = None
#the id of the client on the ATT platform, used to connect to the http & mqtt servers
ClientId = None
#the id of the device provided by the ATT platform
DeviceId = None
#the key that the ATT platform generated for the specified client
ClientKey = None

#connect with the http server
def connect(httpServer="att-1.apphb.com"):
    global _httpClient, _httpServerName                                         # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient = httplib.HTTPConnection(httpServer)
    _httpServerName = httpServer
    print("connected with http server")

def addAsset(name, description, isActuator, assetType):
    body = '{"name":"' + name + '","description":"' + description + '","is":"'
    if isActuator:
        body = body + 'actuator'
    else:
        body = body + 'sensor'
    body = body + '","profile": {"type":"' + assetType + '" } }';
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    _httpClient.request("POST", body, None, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())

#start the mqtt client and make certain that it can receive data from the IOT platform
def subscribe(mqttServer = "188.64.53.92", port = 1883):
    global _mqttClient, _httpClient                                             # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient.close()
    _httpClient = None                                                             #the http client is no longer used, so free the mem.
    _mqttClient = mqtt.Client()
    _mqttClient.on_connect = on_connect
    _mqttClient.on_message = on_MQTTmessage

    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()

def send(value, sensorId):
    if ClientId is None:
        print("ClientId not specifie")
        raise Exception("ClientId not specified")
    if DeviceId is None:
        print("device id not specified")
        raise Exception("DeviceId not specified")
    if sensorId is None:
        print("sensor id not specified")
        raise Exception("sensorId not specified")
    timestamp = calendar.timegm(time.gmtime())                                # we need the current epoch time so we can provide the correct time stamp.
    toSend = timestamp + "|" + value                                            # build the string that contains the data that we want to send
    topic = "/f/" + ClientId + "/s/" + DeviceId + "/" + sensorId            # also need a topic to publish to
    _mqttClient.publish(topic, toSend, 0, False)