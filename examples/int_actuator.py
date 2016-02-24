# -*- coding: utf-8 -*-

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)
import logging
logging.getLogger().setLevel(logging.INFO)

import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.DeviceId = "put your device id here"
IOT.ClientId = "put your client id here"
IOT.ClientKey = "put your client key here"

In1Name = "Put the name of your sensor"                                #name of the button
In1Id = 1                                                            #the id of the button, don't uses spaces. required for the att platform
Out1Name = "Put the name of your actuator"
Out1Id = 2


#callback: handles values sent from the cloudapp to the device
def on_message(id, value):
    global nextVal
    if id.endswith(str(Out1Id)) == True:			
        print("value received: " + value)		  # the value that we receive from the cloud is a string
        IOT.send(value, Out1Id)                #provide feedback to the cloud that the operation was successful, the value is still a string, so we can simply send it back to the cloud.
        nextVal = int(value)					# convert the received data, which is a string, into an integer
    else:
        print("unknown actuator: " + id)
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Id, In1Name, "put your description here", False, "integer")
IOT.addAsset(Out1Id, Out1Name, "put your description here", True, "integer")
IOT.subscribe()                                        		#starts the bi-directional communication

nextVal = 0
#main loop: run as long as the device is turned on
while True:
    print("value: " + str(nextVal))
    IOT.send(str(nextVal), In1Id)
    nextVal = nextVal + 1
    sleep(5)