#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Motion detector experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_arduino_standard_lib as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

sensorName = "PIR"                                              #name of the sensor
sensorPrev = False                                  #previous value of the sensor (only send a value when a change occured)
sensorPin = 2
sensorId = "1"                                      #the id of the button, don't uses spaces. required for the att platform

actuatorName = "LED"
actuatorPin = 4
actuatorId = "2"


#set up the pins
grovepi.pinMode(sensorPin,"INPUT")
grovepi.pinMode(actuatorPin,"OUTPUT")

#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(actuatorId) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(actuatorPin, 1)
            IOT.send("true", actuatorId)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(actuatorPin, 0)
            IOT.send("false", actuatorId)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorId, sensorName, "PIR SENSOR", False, "bool")
IOT.addAsset(actuatorId, actuatorName, "Light Emitting Diode", True, "bool")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    if grovepi.digitalRead(sensorPin) == 1:
        if sensorPrev == False:
            print(sensorName + " activated")
            IOT.send("true", sensorId)
            sensorPrev = True
    elif sensorPrev == True:
        print(sensorName + " deactivated")
        IOT.send("false", sensorId)
        sensorPrev = False
    sleep(.3)

