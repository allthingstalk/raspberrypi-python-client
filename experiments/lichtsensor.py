#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving lichtsensor experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_python_standard_lib as IOT   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

lichtSensor = 0                                  #the PIN number of the lichtsensor, also used to construct a Unique assetID (DeviceID+nr)

#set up the pins
grovepi.pinMode(lichtSensor,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(lichtSensor, "lichtSensor", "Licht Sensor", False, "int")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        lichtValue =  grovepi.analogRead(lichtSensor)
        print( "LichtSensor = " + str(lichtValue))
        IOT.send(lichtValue, lichtSensor)
        sleep(5)

    except IOError:
        print ""
