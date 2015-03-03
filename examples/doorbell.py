#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Doorbell experiment
# Important: before running this experiment, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT   						   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

sensorPrev = False

doorBell = 2						# The Pin number of the Shield, also used to construct the AssetID



#set up the pins
grovepi.pinMode(doorBell,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(doorBell, "DoorBell", "DoorBell", False, "bool")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        if grovepi.digitalRead(doorBell) == 1:
            if sensorPrev == False:
                print("DoorBell  activated")
                IOT.send("true", doorBell)
                sensorPrev = True
        elif sensorPrev == True:
            print("DoorBell  deactivated")
            IOT.send("false", doorBell)
            sensorPrev = False
        sleep(.3)

    except IOError:
        print ""
