# -*- coding: utf-8 -*-

#for documentation about the mqtt lib, check https://pypi.python.org/pypi/paho-mqtt/0.9
import paho.mqtt.client as mqtt                # provides publish-subscribe messaging support
import calendar                                # for getting the epoch time
import time                                    # gets the current time
import httplib                                 # for http comm


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    if rc == 0:
        msg = "Connected to mqtt broker with result code "+str(rc)
        print(msg)
        if DeviceId is None:
            print("device id not specified")
            raise Exception("DeviceId not specified")
        topic = "/m/" + ClientId + "/#"
        print("subscribing to: " + topic)
        result = client.subscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        print(result)
        topic = "/s" + topic[2:]
        print("subscribing to: " + topic)
        result = client.subscribe(topic)
        print(result)
    else:
        print("failed to connect to mqtt broker")


# The callback for when a PUBLISH message is received from the server.
def on_MQTTmessage(client, userdata, msg):
    payload = str(msg.payload)
    print("Incomming message - topic: " + msg.topic + ", payload: " + payload)
    topicParts = msg.topic.split("/")
    if on_message is not None:
        on_message(topicParts[-1], msg.payload)

def on_MQTTSubscribed(client, userdata, mid, granted_qos):
    print("subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))


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
    body = body + '","profile": {"type":"' + assetType + '" },"deviceId":"' + DeviceId + '" }'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}

    print("HTTP POST: /api/asset?idFromName=true")
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)

    _httpClient.request("POST", "/api/asset?idFromName=true", body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())

#start the mqtt client and make certain that it can receive data from the IOT platform
#mac: the mac address of the device to uniquely identify it accross the network.
#mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
#port: (optional) the port number to communicate on with the mqtt server.
def subscribe(mac, mqttServer = "188.64.53.92", port = 1883):
    global _mqttClient, _httpClient                                             # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient.close()
    _httpClient = None                                                             #the http client is no longer used, so free the mem.
    _mqttClient = mqtt.Client(mac)
    _mqttClient.on_connect = on_connect
    _mqttClient.on_message = on_MQTTmessage
    _mqttClient.on_subscribe = on_MQTTSubscribed

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
    toSend = str(timestamp) + "|" + str(value)                                            # build the string that contains the data that we want to send
    topic = "/f/" + ClientId + "/s/" + DeviceId + "/" + sensorId            # also need a topic to publish to
    _mqttClient.publish(topic, toSend, 0, False)