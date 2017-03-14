# -*- coding: utf-8 -*-

#   Copyright 2014-2016 AllThingsTalk
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

#for documentation about the mqtt lib, check https://pypi.python.org/pypi/paho-mqtt/0.9
import paho.mqtt.client as mqtt                # provides publish-subscribe messaging support
import calendar                                # for getting the epoch time
from datetime import datetime, tzinfo, timedelta    # for json date time
import time                                    # gets the current time
import httplib                                 # for http comm
import socket                                  # for checking if there is support for https
import types as types                          # to check on type info
import json                                    # in case the data we need to send is complex
import logging


# The callback for when the client receives a CONNACK response from the server.
def _on_connect(client, userdata, rc):
    if rc == 0:
        msg = "Connected to mqtt broker with result code "+str(rc)
        logging.info(msg)
        if DeviceId is None:
            logging.info("device id not specified")
            raise Exception("DeviceId not specified")
        topic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/+/command"
        logging.info("subscribing to: " + topic)
        result = client.subscribe(topic)                                                    #Subscribing in _on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        logging.info(str(result))                                                           # result is not a string on all platforms.
    else:
        logging.error("Failed to connect to mqtt broker: "  + mqtt.connack_string(rc))


# The callback for when a PUBLISH message is received from the server.
def _on_MQTTmessage(client, userdata, msg):
    payload = str(msg.payload)
    logging.info("Incoming message - topic: " + msg.topic + ", payload: " + payload)
    topicParts = msg.topic.split("/")
    if on_message is not None:
        on_message(topicParts[-2], msg.payload)										#we want the second last value in the array, the last one is 'command'

def _on_MQTTSubscribed(client, userdata, mid, granted_qos):
    logging.info("Subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))


#private reference to the mqtt client object for which we reserve a mem loc from the start
_mqttClient = None
#_httpServerName = None
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

def connect(httpServer="api.allthingstalk.io", secure = False):
    '''
    Create a HTTP connection with the server
    :param httpServer: The dns name of the server to use for HTTP communication
    :param secure: When true, an SSL connection will be used, if available.
    '''
    global _httpClient#, _httpServerName                                         # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if secure and socket.ssl:
        _httpClient = httplib.HTTPSConnection(httpServer)
    else:
        _httpClient = httplib.HTTPConnection(httpServer)
    #_httpServerName = httpServer
    logging.info("connected with http server")

def addAsset(id, name, description, isActuator, assetType, style = "Undefined"):
    '''
    Create or update the specified asset. Call this function after calling 'connect' for each asset that you want to use.
    :param id: `string or number` the local id of the asset
    :param name: `basestring` the label that should be used to show on the website
    :param description: `basestring` a description of the asset
    :param isActuator: `boolean` True if this is an actuator. When False, it's created as a Sensor
    :param assetType: `string` the type of the asset, possible values: 'integer', 'number', 'boolean', 'text', None (defaults to string, when the asset already exists, the website will not overwrite any changes done manually on the site). Can also be a complete profile definition as a json string (see http://allthingstalk.com/docs/cloud/concepts/assets/profiles/) example: '{"type": "integer", "minimum": 0}'.
    :param style: `basestring` possible values: 'Primary', 'Secondary', 'Config', 'Battery'
    '''

    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = '{"name":"' + name + '","description":"' + description + '", "style": "' + style + '","is":"'
    if isActuator:
        body += 'actuator'
    else:
        body += 'sensor'
    if not assetType:
        body += '" }'
    elif assetType[0] == '{':                 # if the asset type is complex (starts with {', then render the body a little different
        body = body + '","profile":' + assetType + '}'
    else:
        body = body + '","profile": {"type":"' + assetType + '"}}'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/device/" + DeviceId + "/asset/" +  str(id)
	
    logging.info("HTTP PUT: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY:" + body)

    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    logging.info(response.read())


def updateDevice(name, description, activityEnabled = False):
    '''
    Updates the definition of the device.
    :param name: The name of the device
    :param description: the description for the device
    :param activityEnabled: When True, historical data will be stored on the db, otherwise only the last received value is stored.
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = '{"name":"' + name + '","description":"' + description + '","activityEnabled":' + str(activityEnabled).lower() + '}'
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/Device/" + DeviceId

    logging.info("HTTP PUT: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    logging.info(jsonStr)

def deleteDevice():
    '''
    Deletes the currently loaded device from the cloud.  After this function, the global DeviceId will be reset to None
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/Device/" + DeviceId

    logging.info("HTTP DELETE: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY: None")
    _httpClient.request("DELETE", url, "", headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    if response.status == 204:
        logging.info(jsonStr)
        DeviceId = None
    else:
        logging.error(jsonStr)

def getPrimaryAsset():
    '''
    Returns, as a list, the asset(s) assigned to the device as being "primary", that is, these assets represent the main functionality of the device. Ex: a wall plug - powerswithch  can have many assets, but it's primary function is to switch on-off
    :return: A json array contains all the assets that the cloud knows of for the current device and which have been labeled to be primary '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    url = "/Device/" + DeviceId + "/assets?style=primary"
    return _doHTTPGet(url, "")


def _buildPayLoadHTTP(value):
    data = {"value": value, "at": datetime.utcnow().isoformat() + 'Z'}
    return json.dumps(data)



def sendValueHTTP(value, assetId):
    '''
    Sends a new value for an asset over http. This function is similar to send, accept that the latter uses mqtt while this function uses HTTP
    Parameters are the same as for the send function.
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    body = _buildPayLoadHTTP(value)
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/device/" + DeviceId + "/asset/" + str(assetId) + "/state"

    logging.info("HTTP PUT: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    logging.info(jsonStr)

def sendCommandToHTTP(value, assetId):
    '''
    Sends a command to an asset on another device using http(s). The assetId should be the full id (string), as seen on the cloud app.
    > You can only send commands to actuators that belong to devices in the same account as this device.
    ex: sendCommandTo('122434545abc112', 1)
    :param value: same as for 'send' and 'sendValueHTTP'
    :param assetId: `basestring` the id of the asset to send the value to. This id must be the full id as found on the cloud app
    '''
    body = {"value": value }
    body = json.dumps(body)

    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    url = "/asset/" +  assetId + "/command"

    logging.info("HTTP PUT: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY:" + body)
    _httpClient.request("PUT", url, body, headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr = response.read()
    logging.info(jsonStr)

def getAssetState(asset, device = None):
    '''
    Gets the last recorded value for the specified asset.
    When device is ommitted (or None), the current device is used, otherwise the device with the specified id is used.
    :param device: The id of the device to use. When None, the current device is queried.
    :param asset: `string or int` The id of the d
    :return: a json object containing the last recorded data.
    '''
    if not device:
        if not DeviceId:
            raise Exception("DeviceId not specified")
        device = DeviceId
    url = "/device/" + device + "/asset/" + str(asset) + "/state"
    return _doHTTPGet(url, "")


def _doHTTPGet(url, content):
    headers = {"Content-type": "application/json", "Auth-ClientKey": ClientKey, "Auth-ClientId": ClientId}
    logging.info("HTTP GET: " + url)
    logging.info("HTTP HEADER: " + str(headers))
    logging.info("HTTP BODY: None")
    _httpClient.request("GET", url, content, headers)
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    if response.status == 200:
        logging.info(jsonStr)
        return json.loads(jsonStr)
    else:
        logging.error(jsonStr)
        return None


def getAssets():
    '''
    Get the list of assets that are known for this device in the cloud.
    :return: a json array containing all the assets.
    '''
    global DeviceId
    if not DeviceId:
        raise Exception("DeviceId not specified")
    url = "/Device/" + DeviceId + "/assets"

    return _doHTTPGet(url, "")

def closeHttp():
    '''
    Closes the http connection, if it was open
    :return: None
    '''
    global _httpClient  # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if _httpClient:
        _httpClient.close()
        _httpClient = None  # the http client is no longer used, so free the mem.

def subscribe(mqttServer = "api.allthingstalk.io", port = 1883, secure = False, certFile = 'cacert.pem'):
    '''
    Sets up everything for the pub-sub client: create the connection, provide the credentials and register for any possible incoming data. This function also closes the http connection if it was opened.
    If you need both http and mqtt opened at the same time, it's best to open mqtt first, then open the http connection.
    :param mqttServer:  the address of the mqtt server. Only supply this value if you want to a none standard server. Default = api.AllThingsTalk.io
    :param port: the port number to communicate on with the mqtt server. Default = 1883
    :param secure: When true, an SSL connection is used. Default = False.  When True, use port 8883 on api.AllThingsTalk.io
    :param certFile: certfile is a string pointing to the PEM encoded client certificate and private keys respectively.
    
    > If either of these files in encrypted and needs a password to decrypt it, Python will ask for the password at the command line. It is currently not possible to define a callback to provide the password.
    SSL can only be used when the mqtt lib has been compiled with support for SSL.
    '''
    global _mqttClient                                             # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars

    closeHttp()                                                     # when starting the mqtt connection, no more need of the http connection.
    if len(DeviceId) > 23:
        mqttId = DeviceId[:23]
    else:
        mqttId = DeviceId
    _mqttClient = mqtt.Client(mqttId)
    _mqttClient.on_connect = _on_connect
    _mqttClient.on_message = _on_MQTTmessage
    _mqttClient.on_subscribe = _on_MQTTSubscribed
    if ClientId is None:
        logging.info("ClientId not specified, can't connect to broker")
        raise Exception("ClientId not specified, can't connect to broker")
    brokerId = ClientId + ":" + ClientId
    _mqttClient.username_pw_set(brokerId, ClientKey)
    if secure and socket.ssl:
        # todo: temporary check making certain that no certificate is used on api.allthingstalk.com, not yet supported. Will still work on broker.smartliving.io
        if mqttServer == "api.allthingstalk.com":
            logging.warn("SSL is not yet supported on api.allthingstalk.com, please use broker.smartliving.io. This will be corrected in the near future.")
        else:
            _mqttClient.tls_set(certFile)
    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()

def closeMqtt():
    '''
    Closes the mqtt connection, if opened.
    :return: None
    '''
    global _mqttClient
    if _mqttClient:
        _mqttClient.disconnect()
        _mqttClient = None

def _buildPayLoad(value):
    typeOfVal = type(value)
    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType, types.StringType]:      # if it's a basic type: send as csv, otherwise as json.
        timestamp = calendar.timegm(time.gmtime())                                # we need the current epoch time so we can provide the correct time stamp.
        return str(timestamp) + "|" + str(value).lower()                                          # build the string that contains the data that we want to send
    else:
        data = {  "value": value, "at": datetime.utcnow().replace(tzinfo=simple_utc()).isoformat() }
        return json.dumps(data)
	
	
def send(value, assetId):
    '''
    Use this function to send a data value to the cloud server, using MQTT, for the asset with the specified id as provided by the IoT platform.
    :param value: `number, string, boolean, object or list` the value to send. This can be in the form of a string, int, double, bool or python object/list All primitive values are converted to a lower case string, ex: 'true' or 'false'. You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
    :param id: `string or number` the local asset identifier (asset name) of the asset to send the value to, usually the pin number. This is the same value used while creating/updating the asset through the function 'addAsset' ex: 1
    '''
    if ClientId is None:
        logging.error("ClientId not specified")
        raise Exception("ClientId not specified")
    if DeviceId is None:
        logging.error("device id not specified")
        raise Exception("DeviceId not specified")
    if assetId is None:
        logging.error("sensor id not specified")
        raise Exception("sensorId not specified")
    toSend = _buildPayLoad(value)
    topic = "client/" + ClientId + "/out/device/" + DeviceId + "/asset/" + str(assetId)  + "/state"		  # also need a topic to publish to
    logging.info("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)

def sendCommandTo(value,device, actuator):
    '''
    Send a command to the specified actuator. The device has to be in the same account as this device.
    :param value: the value to send
    :param device: the device id to send it to.
    :param actuator: the local id of the actuator (name)
    '''
    if ClientId is None:
        logging.error("ClientId not specified")
        raise Exception("ClientId not specified")
    if device is None:
        logging.error("device id not specified")
        raise Exception("device not specified")
    if actuator is None:
        logging.error("actuator id not specified")
        raise Exception("actuator not specified")
    if actuator is None:
        logging.error("sensor id not specified")
        raise Exception("sensorId not specified")
    toSend = str(value)
    topic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/" + str(actuator)  + "/command"		  # also need a topic to publish to
    logging.info("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)


class simple_utc(tzinfo):
    '''
    Handling time zone info.
    '''
    def tzname(self):
        return "UTC"
    def utcoffset(self, dt):
        return timedelta(0)
