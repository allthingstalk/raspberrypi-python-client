#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2014-2016 AllThingsTalk
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# AllThingsTalk lightsensor experiment
# Important: before running this demo, make certain that grovepi & ATT_IOT
# are in the same directory as this script, or installed so that they are globally accessible
import logging
logging.getLogger().setLevel(logging.INFO)

import grovepi                                     #provides pin support
import att_iot_client.ATT_IOT as IOT               #provide cloud support
from time import sleep                             #pause the app

#set up the AllThingsTalk IoT platform
IOT.DeviceId = ""
IOT.ClientId = ""
IOT.ClientKey = ""

lightSensor = 0                                  #the PIN number of the lichtsensor, also used to construct a Unique assetID (DeviceID+nr)

#set up the pins
grovepi.pinMode(lightSensor,"INPUT")

#callback: handles values sent from the cloudapp to the device

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(lightSensor, "lightSensor", "Light Sensor", False, "integer")
IOT.subscribe()              							#starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    try:
        lightValue =  grovepi.analogRead(lightSensor)
        print( "LightSensor = " + str(lightValue))
        IOT.send(lightValue, lightSensor)
        sleep(5)

    except IOError:
        print ""
