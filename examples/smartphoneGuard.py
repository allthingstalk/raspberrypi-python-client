#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Smartphone Unplugged experiment
# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT   						   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""


vMotor = 2                                     # Shield pin nr & construct for AssetID

#set up the pins
grovepi.pinMode(vMotor,"OUTPUT")


#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(str(vMotor)) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(vMotor, 1)
            IOT.send("true", vMotor)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(vMotor, 0)
            IOT.send("false", vMotor)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(vMotor, "vMotor", "Vibration Motor", True, "bool")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    sleep(.3)
