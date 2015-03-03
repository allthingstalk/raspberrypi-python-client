#!/usr/bin/env python
# -*- coding: utf-8 -*-

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)
#also make certain that ATT_IOT is in the same directory as this script.

import RPi.GPIO as GPIO                            #provides pin support
import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform

IOT.DeviceId = "YourDeviceIdHere"
IOT.ClientId = "YourClientIdHere"
IOT.ClientKey = "YourClientKeyHere"
IOT.BrokerUserId = "put your username for the broker here"

SensorName = "Button"                                #name of the button
SensorPrev = False                                   #previous value of the button
SensorPin = 13

ActuatorName = "Diode"
ActuatorPin = 8

#setup GPIO using Board numbering
#alternative:  GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

#set up the pins
GPIO.setup(SensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #, pull_up_down=GPIO.PUD_DOWN
GPIO.setup(ActuatorPin, GPIO.OUT)

#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(str(ActuatorPin)) == True:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            GPIO.output(ActuatorPin, True)
            IOT.send("true", ActuatorPin)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            GPIO.output(ActuatorPin, False)
            IOT.send("false", ActuatorPin)                #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(SensorPin, SensorName, "Push button", False, "bool")
IOT.addAsset(ActuatorPin, ActuatorName, "Light Emitting Diode", True, "bool")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    if GPIO.input(SensorPin) == 0:                        #for PUD_DOWN, == 1
        if SensorPrev == False:
            print(SensorName + " activated")
            IOT.send("true", SensorPin)
            SensorPrev = True
    elif SensorPrev == True:
        print(SensorName + " deactivated")
        IOT.send("false", SensorPin)
        SensorPrev = False
    sleep(1)
