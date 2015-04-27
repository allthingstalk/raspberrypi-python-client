#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import ATT_IOT as IOT   #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.DeviceId = "YourDeviceIdHere"
IOT.ClientId = "YourClientIdHere"
IOT.ClientKey = "YourClientKeyHere"

#Define each asset below. provide a Name and Pin. The Pin number is used to define the Pin number on your raspberry Pi shield
#and to create a unique assetId which is a combination of deviceID+Pin number. The Pin number can be any value between (0 - 2^63)

sensorName = "Button"            		    #name of the sensor
sensorPin = 2
sensorPrev = False                                  #previous value of the sensor (only send a value when a change occured)


#set up the pins

#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    print("unknown actuator: " + id)

IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorPin, sensorName, "location info", False, "{\"type\": \"object\",\"properties\": {\"latitude\": { \"type\": \"number\" },\"longitude\": { \"type\": \"number\" }}}")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        value = {'latitude': 1, 'longitude': 2}
        IOT.send(value, sensorPin)
        sleep(2)

    except IOError:
        print ""