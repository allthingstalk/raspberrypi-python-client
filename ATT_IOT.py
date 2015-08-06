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

def addAsset(id, name, description, isActuator, assetType, style = "Undefined"):
    '''Add an asset to the device.'''

    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = '{"name":"' + name + '","description":"' + description + '", "style": "' + style + '","is":"'
    if isActuator:
        body = body + 'actuator'
    else:
        body = body + 'sensor'
    if assetType[0] == '{':                 # if the asset type is complex (starts with {', then render the body a little different
        body = body + '","profile":' + assetType + ',"deviceId":"' + DeviceId + '" }'
    else:
        body = body + '","profile": {"type":"' + assetType + '" },"deviceId":"' + DeviceId + '" }'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/asset/" + DeviceId + str(id)
	
    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)

    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    print(response.read())

def createDevice(name, description, activityEnabled = False):
    '''creates a new device. The Id of the device will be stored in DeviceId'''
    global DeviceId
    body = '{"name":"' + name + '","description":"' + description + '","activityEnabled":' + str(activityEnabled).lower() + '}'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/Device"

    print("HTTP POST: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)
    _httpClient.request("POST", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)
    if response.status == 201:
        d = json.loads(jsonStr)
        DeviceId = d["id"]


def updateDevice(name, description, activityEnabled = False):
    '''updates the definition of the device'''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = '{"name":"' + name + '","description":"' + description + '","activityEnabled":' + str(activityEnabled).lower() + '}'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/Device/" + DeviceId

    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)

def deleteDevice():
    '''
        Deletes the currently loaded device from the cloud.  After this function, the global DeviceId will be reset
        to None
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/Device/" + DeviceId

    print("HTTP DELETE: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY: None")
    _httpClient.request("DELETE", url, "", headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)
    if response.status == 204:
        DeviceId = None

def getPrimaryAsset():
    '''returns,as a list, the asset(s) assigned to the device as being "primary", that is, these assets represent the main functionality
       of the device. Ex: a wall plug - powerswithch  can have many assets, but it's primary function is to switch on-off'''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    url = "/Device/" + DeviceId + "/assets?style=primary"
    return doHTTPGet(url, "")


def _buildPayLoadHTTP(value):
    data = {"value": value, "at": datetime.utcnow().isoformat()}
    return json.dumps(data)



def sendValueHTTP(value, assetId):
    '''Sends a new value for an asset over http. This function is similar to send, accept that the latter uses mqtt
       while this function uses HTTP'''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = _buildPayLoadHTTP(value)
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/asset/" +  DeviceId + str(assetId) + "/state"

    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)

def sendCommandTo(value, assetId):
    '''
        Sends a command to an asset on another device.
        The assetId should be the full id (string), as seen on the cloud app.
        Note: you can only send commands to actuators that belong to devices in the same account as this device.

        ex: sendCommandTo('122434545abc112', 1)
    '''
    typeOfVal = type(value)
    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType, types.StringType]:      # if it's a basic type: send as csv, otherwise as json.
        body = str(value)
    else:
        body = json.dumps(value)

    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/asset/" +  assetId + "/command"

    print("HTTP PUT: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)

def getAssetState(asset):
    '''Gets the last recorded value for the specified asset.
       When the asset is an int, it is presumed to be a local asset of this device. If it's a string, the asset
       can be of an other device.
    :type asset: string or int
    :returns a json object containing the last recorded data.
    '''
    if type(asset) == types.IntType:
        global DeviceId
        if not DeviceId:
            raise Exception("DeviceId not specified")
        url = "/asset/" + DeviceId + str(asset) +  "/state"
    else:
        url = "/asset/" + asset + "/state"
    return doHTTPGet(url, "")


def doHTTPGet(url, content):
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    print("HTTP GET: " + url)
    print("HTTP HEADER: " + str(headers))
    print("HTTP BODY: None")
    _httpClient.request("GET", url, content, headers)
    response = _httpClient.getresponse()
    print(response.status, response.reason)
    jsonStr =  response.read()
    print(jsonStr)
    if response.status == 200:
        return json.loads(jsonStr)
    else:
        return None


def getAssets():
    '''
        gets the list of assets that are known for this device in the cloud
        :returns a json array containing all the assets.
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    url = "/Device/" + DeviceId + "/assets"

    return doHTTPGet(url, "")

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
        return str(timestamp) + "|" + str(value).lower()                                          # build the string that contains the data that we want to send
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
