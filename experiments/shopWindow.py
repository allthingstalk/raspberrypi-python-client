#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Shop Window experiment
# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT  							   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""


Led = 4

#set up the pins
grovepi.pinMode(Led,"OUTPUT")


#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(str(Led)) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(Led, 1)
            IOT.send("true", Led)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(Led, 0)
            IOT.send("false", Led)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(Led, "Shop Light", "Shop Window Light", True, "boolean")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    sleep(.3)
