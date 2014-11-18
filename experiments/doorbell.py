#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Doorbell experiment
# Important: before running this experiment, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_arduino_standard_lib as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

sensorName = "DoorBell"                                                   #name of the senso   sensorPrev = False                                  #previous value of the sensor (only send a value when a change occured)
sensorPrev = False
sensorPin = 2
sensorId = "1"                                      #the id of the button, don't uses spaces. required for the att platform


#set up the pins
grovepi.pinMode(sensorPin,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorId, sensorName, "DoorBell", False, "bool")
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

