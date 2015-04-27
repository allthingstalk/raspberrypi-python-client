# -*- coding: utf-8 -*-

#for documentation about the mqtt lib, check https://pypi.python.org/pypi/paho-mqtt/0.9
import paho.mqtt.client as mqtt                # provides publish-subscribe messaging support
import calendar                                # for getting the epoch time
from datetime import datetime                  # for json date time
import time                                    # gets the current time
import httplib                                 # for http comm
import types as types                          # to check on type info
import json                                    # in case the data we need to send is complex


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    if rc == 0:
        msg = "Connected to mqtt broker with result code "+str(rc)
        print(msg)
        if DeviceId is None:
            print("device id not specified")
            raise Exception("DeviceId not specified")
        topic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/+/command"
        print("subscribing to: " + topic)
        result = client.subscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        print(result)
    else:
        print("Failed to connect to mqtt broker: "  + mqtt.connack_string(rc))


# The callback for when a PUBLISH message is received from the server.
def on_MQTTmessage(client, userdata, msg):
    payload = str(msg.payload)
    print("Incoming message - topic: " + msg.topic + ", payload: " + payload)
    topicParts = msg.topic.split("/")
    if on_message is not None:
        on_message(topicParts[-2], msg.payload)										#we want the second last value in the array, the last one is 'command'

def on_MQTTSubscribed(client, userdata, mid, granted_qos):
    print("Subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))


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

def connect(httpServer="api.smartliving.io"):
    '''connect with the http server'''
    global _httpClient, _httpServerName                                         # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient = httplib.HTTPConnection(httpServer)
    _httpServerName = httpServer
    print("connected with http server")

def addAsset(id, name, description, isActuator, assetType):
    body = '{"name":"' + name + '","description":"' + description + '","is":"'
    if isActuator:
        body = body + 'actuator'
    else:
        body = body + 'sensor'
    if assetType[0] == '{':                 # if the asset type is complex (starts with {', then render the body a little different
        body = body + '","profile":' + assetType + ',"deviceId":"' + DeviceId + '" }'
    else:
        body = body + '","profile": {"type":"' + assetType + '" },"deviceId":"' + DeviceId + '" }'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/api/asset/" + DeviceId + str(id) 
	
    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)

    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())


def subscribe(mqttServer = "broker.smartliving.io", port = 1883):
    '''start the mqtt client and make certain that it can receive data from the IOT platform
	   mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
	   port: (optional) the port number to communicate on with the mqtt server.
    '''
    global _mqttClient, _httpClient                                             # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient.close()
    _httpClient = None                                                             #the http client is no longer used, so free the mem.
    if len(DeviceId) > 23:
        mqttId = DeviceId[:23]
    else:
        mqttId = DeviceId
    _mqttClient = mqtt.Client(mqttId)
    _mqttClient.on_connect = on_connect
    _mqttClient.on_message = on_MQTTmessage
    _mqttClient.on_subscribe = on_MQTTSubscribed
    if ClientId is None:
        print("ClientId not specified, can't connect to broker")
        raise Exception("ClientId not specified, can't connect to broker")
    brokerId = ClientId + ":" + ClientId
    _mqttClient.username_pw_set(brokerId, ClientKey)

    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()

def _buildPayLoad(value):
    typeOfVal = type(value)
    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType, types.StringType]:      # if it's a basic type: send as csv, otherwise as json.
        timestamp = calendar.timegm(time.gmtime())                                # we need the current epoch time so we can provide the correct time stamp.
        return str(timestamp) + "|" + str(value)                                            # build the string that contains the data that we want to send
    else:
        data = {  "value": value, "at": datetime.utcnow().isoformat() }
        return json.dumps(data)
	
	
def send(value, assetId):
    if ClientId is None:
        print("ClientId not specified")
        raise Exception("ClientId not specified")
    if DeviceId is None:
        print("device id not specified")
        raise Exception("DeviceId not specified")
    if assetId is None:
        print("sensor id not specified")
        raise Exception("sensorId not specified")
    toSend = _buildPayLoad(value)
    topic = "client/" + ClientId + "/out/asset/" + DeviceId + str(assetId)  + "/state"		  # also need a topic to publish to
    print("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)
