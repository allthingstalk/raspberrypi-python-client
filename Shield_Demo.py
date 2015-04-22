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

actuatorName = "Diode"
actuatorPin = 4

#set up the pins
grovepi.pinMode(sensorPin,"INPUT")
grovepi.pinMode(actuatorPin,"OUTPUT")

#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(str(actuatorPin)) == True:
        value = value.lower()                        	#make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            grovepi.digitalWrite(actuatorPin, 1)
            IOT.send("true", actuatorPin)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            grovepi.digitalWrite(actuatorPin, 0)
            IOT.send("false", actuatorPin)               #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorPin, sensorName, "Push button", False, "boolean")
IOT.addAsset(actuatorPin, actuatorName, "Light Emitting Diode", True, "boolean")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        if grovepi.digitalRead(sensorPin) == 1:
            if sensorPrev == False:
                print(sensorName + " activated")
                IOT.send("true", sensorPin)
                sensorPrev = True
        elif sensorPrev == True:
            print(sensorName + " deactivated")
            IOT.send("false", sensorPin)
            sensorPrev = False
        sleep(.3)

    except IOError:
        print ""