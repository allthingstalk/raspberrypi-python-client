#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving lightsensor experiment
# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT 							   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving IoT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

lightSensor = 0                                  #the PIN number of the lichtsensor, also used to construct a Unique assetID (DeviceID+nr)

#set up the pins
grovepi.pinMode(lightSensor,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(lightSensor, "lightSensor", "Light Sensor", False, "integer")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        lightValue =  grovepi.analogRead(lightSensor)
        print( "LightSensor = " + str(lightValue))
        IOT.send(lightValue, lightSensor)
        sleep(5)

    except IOError:
        print ""
