# -*- coding: utf-8 -*-
# not yet supported
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
    else:
        print("Failed to connect to mqtt broker " )


# The callback for when a PUBLISH message is received from the server.
def on_MQTTmessage(client, userdata, msg):
    payload = str(msg.payload)
    print("Incoming message - topic: " + msg.topic + ", payload: " + payload)
    topicParts = msg.topic.split("/")
    if on_message is not None:
        on_message(topicParts[-2], msg.payload)									#we want the second last value in the array, the last one is 'command'

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
#the key that the ATT platform generated for the specified client
ClientKey = None

#connect with the http server
def connect(httpServer="api.smartliving.io"):
    global _httpClient, _httpServerName                                         # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    _httpClient = httplib.HTTPConnection(httpServer)
    _httpServerName = httpServer
    print("connected with http server")

def addAsset(id, deviceId, name, description, isActuator, assetType):
    body = '{"name":"' + name + '","description":"' + description + '","is":"'
    if isActuator:
        body = body + 'actuator'
    else:
        body = body + 'sensor'
    body = body + '","profile": {"type":"' + assetType + '" },"deviceId":"xbee_' + deviceId + '" }'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/api/asset/xbee_" + deviceId + "_" + str(id)
	
    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)

    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())

#creates a new device in the IOT platform. The deviceId gets appended with the value "xbee_"
#if the device already exists, the function will fail
#returns True if the operation was succesful, otherwise False
def addDevice(deviceId, name, description):
    body = '{"id":"xbee_' + deviceId + '","name":"' + name + '","description":"' + description + '" }'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/api/device"
	
    print("HTTP POST: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)

    _httpClient.request("POST", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())
    return response.status == 201

#subscribe to the pub-sub topic for the specified device, so we can receive
#changes from the IOT platform
def subscribeDevice(deviceId):
    topic = "client/" + ClientId + "/in/device/xbee_" + deviceId + "/+/command"                            #subscribe to the topics for the device
    print("subscribing to: " + topic)
    result = _mqttClient.subscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    print(result)

#checks if the device already exists in the IOT platform.
#returns True when it already exists, otherwise False
def deviceExists(deviceId):
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/api/device/xbee_" + deviceId
	
    print("HTTP GET: " + url)
    print("HTTP HEADER: " + str(headers))

    _httpClient.request("GET", url, "", headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())
    return response.status == 200

#start the mqtt client and make certain that it can receive data from the IOT platform
#mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
#port: (optional) the port number to communicate on with the mqtt server.
def subscribe(mqttServer = "broker.smartliving.io", port = 1883):
    global _mqttClient                                             # we assign to this var first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if len(ClientId) > 23:
        mqttId = ClientId[:23]
    else:
        mqttId = ClientId
    _mqttClient = mqtt.Client(mqttId)
    _mqttClient.on_connect = on_connect
    _mqttClient.on_message = on_MQTTmessage
    _mqttClient.on_subscribe = on_MQTTSubscribed
    if ClientId is None:
        print("ClientId not specified, can't connect to broker")
        raise Exception("ClientId not specified, can't connect to broker")
    brokerId = ClientId + ":" + ClientId
    _mqttClient.username_pw_set(brokerId, ClientKey);
	
    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()

def send(value, deviceId, assetId):
    if ClientId is None:
        print("ClientId not specifie")
        raise Exception("ClientId not specified")
    if assetId is None:
        print("sensor id not specified")
        raise Exception("sensorId not specified")
    timestamp = calendar.timegm(time.gmtime())                                # we need the current epoch time so we can provide the correct time stamp.
    toSend = str(timestamp) + "|" + str(value)                                            # build the string that contains the data that we want to send
    topic = "client/" + ClientId + "/out/asset/xbee_" + deviceId + "_" + str(assetId) + "/state" # also need a topic to publish to
    print("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)
