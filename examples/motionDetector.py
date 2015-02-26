#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Motion detector experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_python_standard_lib as IOT   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

Pir = 2						#Shield PIN nr & used to construct assetID
Led = 4						#Shield PIN nr & used to construct assetID

Pir_Prev = False

#set up the pins
grovepi.pinMode(Pir,"INPUT")
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
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(Pir, "PIR", "PIR SENSOR", False, "bool")
IOT.addAsset(Led, "LED", "Light Emitting Diode", True, "bool")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        if grovepi.digitalRead(Pir) == 1:
            if Pir_Prev == False:
                print("PIR activated")
                IOT.send("true", Pir)
                Pir_Prev = True
        elif Pir_Prev == True:
            print("PIR deactivated")
            IOT.send("false", Pir)
            Pir_Prev = False
        sleep(.3)

    except IOError:
        print ""

