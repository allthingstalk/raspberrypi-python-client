#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Shop Window experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_arduino_standard_lib as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""


actuatorName1 = "LED"
actuatorPin1 = 4
actuatorId1 = "1"

actuatorName2 = "Buzzer"
actuatorPin2 = 3
actuatorId2 = "2"

actuatorName3 = "LEDBAR"
actuatorPin3 = 2
actuatorId3 = "3"

#set up the pins
grovepi.pinMode(actuatorPin1,"OUTPUT")
grovepi.pinMode(actuatorPin2,"OUTPUT")
grovepi.pinMode(actuatorPin3,"OUTPUT")


#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(actuatorId1) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(actuatorPin1, 1)
            IOT.send("true", actuatorId1)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(actuatorPin1, 0)
            IOT.send("false", actuatorId1)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    elif id.endswith(actuatorId2) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(actuatorPin2, 1)
            IOT.send("true", actuatorId2)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(actuatorPin2, 0)
            IOT.send("false", actuatorId2)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    elif id.endswith(actuatorId3) == True:
        grovepi.analogWrite(actuatorPin3, int(value/100))
        IOT.send(int(value), actuatorId3)                #provide feedback to the cloud that the operation was succesful
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(actuatorId1, actuatorName1, "Light Emitting Diode", True, "bool")
IOT.addAsset(actuatorId2, actuatorName2, "Vibration Motor", True, "bool")
IOT.addAsset(actuatorId3, actuatorName3, "LEB Bar", True, "int")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    sleep(.3)
