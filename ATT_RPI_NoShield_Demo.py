#!/usr/bin/env python
# -*- coding: utf-8 -*-

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)
#also make certain that ATT_IOT is in the same directory as this script.

import RPi.GPIO as GPIO                            #provides pin support
import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.ClientId = "put your client id here"
IOT.ClientKey = "put your client id here"
IOT.DeviceId = "put your device id here"

In1Name = "Put the name of your sensor"                                #name of the button
In1Prev = False                                                        #previous value of the button
In1Pin = 23
In1Id = "1"                                                            #the id of the button, don't uses spaces. required for the att platform

Out1Name = "Put the name of your actuator"
Out1Pin = 24
Out1Id = "2"

#setup GPIO using Board numbering
#alternative:  GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

#set up the pins
GPIO.setup(Out1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #, pull_up_down=GPIO.PUD_DOWN
GPIO.setup(In1Pin, GPIO.OUT)

#callback: handles values sent from the cloudapp to the device
def on_message(actuatorId, value):
    if actuatorId.endswith(Out1Id) == True:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            GPIO.output(Out1Pin, True)
            IOT.send("true", Out1Id)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            GPIO.output(Out1Pin, False)
            IOT.send("false", Out1Id)                #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + actuatorId)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Id, In1Name, "put your description here", False, "bool")
IOT.addAsset(Out1Id, Out1Name, "put your description here", True, "bool")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    if GPIO.input(In1Pin) == 0:                        #for PUD_DOWN, == 1
        if In1Prev == False:
            print(In1Name + " activated")
            IOT.send("true", In1Id)
            In1Prev = True
    elif In1Prev == True:
        print(In1Name + " deactivated")
        IOT.send("false", In1Id)
        In1Prev = False
    sleep(1)