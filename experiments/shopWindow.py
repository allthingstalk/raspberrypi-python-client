#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving Shop Window experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_arduino_standard_lib as IOT   #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""


Led = 4
Buzzer = 3
Ledbar = 2

#set up the pins
grovepi.pinMode(Led,"OUTPUT")
grovepi.pinMode(Buzzer,"OUTPUT")
grovepi.pinMode(Ledbar,"OUTPUT")


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
    elif id.endswith(str(Buzzer)) == True:
        value = value.lower()                           #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(Buzzer, 1)
            IOT.send("true", Buzzer)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(Buzzer, 0)
            IOT.send("false", Buzzer)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    elif id.endswith(str(Ledbar)) == True:
        grovepi.analogWrite(Ledbar, int(value/100))
        IOT.send(int(value), Ledbar)                #provide feedback to the cloud that the operation was succesful
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(Led, "LED", "Light Emitting Diode", True, "bool")
IOT.addAsset(Buzzer, "Buzzer", "Vibration Motor", True, "bool")
IOT.addAsset(Ledbar, "Ledbar", "LEB Bar", True, "int")
IOT.subscribe()                                                                 #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    sleep(.3)
