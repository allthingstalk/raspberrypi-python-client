#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.DeviceId = "put your device id here"
IOT.ClientId = "put your client id here"
IOT.ClientKey = "put your client id here"

sensorName = "Put the name of your sensor"            #name of the sensor
sensorPrev = False                                    #previous value of the sensor (only send a value when a change occured)
sensorPin = 2

actuatorName = "Put the name of your actuator"
actuatorPin = 4


#set up the pins
grovepi.pinMode(sensorPin,"INPUT")
grovepi.pinMode(actuatorPin,"OUTPUT")

#callback: handles values sent from the cloudapp to the device
def on_message(actuatorId, value):
    if actuatorId.endswith(actuatorName) == True:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(actuatorPin, 1)
            IOT.send("true", actuatorName)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(actuatorPin, 0)
            IOT.send("false", actuatorName)                #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + actuatorName)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorName, "put your description here", False, "bool")
IOT.addAsset(actuatorName, "put your description here", True, "bool")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    if grovepi.digitalRead(sensorPin) == 1:
        if sensorPrev == False:
            print(sensorName + " activated")
            IOT.send("true", sensorName)
            sensorPrev = True
    elif sensorPrev == True:
        print(sensorName + " deactivated")
        IOT.send("false", sensorName)
        sensorPrev = False
    sleep(.3)