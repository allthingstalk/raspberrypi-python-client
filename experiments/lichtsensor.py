#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SmartLiving lichtsensor experiment
# Important: before running this demo, make certain that grovepi & allthingstalk_arduino_standard_lib
# are in the same directory as this script, or installed so that they are globally accessible

import grovepi                                     #provides pin support
import allthingstalk_arduino_standard_lib as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the SmartLiving ioT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

sensorName = "lichtSensor"            					#name of the sensor
sensorPin = 0
sensorId = "1"                                      #the id of the button, don't uses spaces. required for the att platform

#set up the pins
grovepi.pinMode(sensorPin,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(sensorId, sensorName, "Licht Sensor", False, "int")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    lichtValue =  grovepi.analogRead(sensorPin)
    print(sensorName + "=" + str(lichtValue))
    IOT.send(lichtValue, sensorId)
    sleep(5)
