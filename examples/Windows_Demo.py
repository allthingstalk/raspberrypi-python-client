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

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)
import logging
logging.getLogger().setLevel(logging.INFO)

import att_iot_client.ATT_IOT as IOT               #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.DeviceId = "VALOlfl1aPpZ7OMV7XnYbB3e"
IOT.ClientId = "testjan"
IOT.ClientKey = "5i4duakv2bq"

In1Name = "Put the name of your sensor"                                #name of the button
In1Id = 1                                                            #the id of the button, don't uses spaces. required for the att platform
Out1Name = "Put the name of your actuator"
Out1Id = 2


#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    if id.endswith(str(Out1Id)) == True:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            print("true on " + Out1Name)
            IOT.send("true", Out1Id)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            print("false on " + Out1Name)
            IOT.send("false", Out1Id)                #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Id, In1Name, "put your description here", False, "boolean")
IOT.addAsset(Out1Id, Out1Name, "put your description here", True, "boolean")
IOT.subscribe()                                        		#starts the bi-directional communication

nextVal = True
#main loop: run as long as the device is turned on
while True:
    if nextVal == True:
        print(In1Name + " activated")
        IOT.send("true", In1Id)
        nextVal = False
    else:
        print(In1Name + " deactivated")
        IOT.send("false", In1Id)
        nextVal = True
    sleep(5)