# -*- coding: utf-8 -*-

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)

import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app


In1Name = "Put the name of your sensor"                                #name of the button
In1Id = "1"                                                            #the id of the button, don't uses spaces. required for the att platform
Out1Name = "Put the name of your actuator"
Out1Id = "2"


#callback: handles values sent from the cloudapp to the device
def on_message(actuatorName, value):
    if actuatorName == Out1Name:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            print("true on " + Out1Name)
        elif value == "false":
            print("false on " + Out1Name)
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + actuatorName)

#set up the ATT internet of things platform
IOT.on_message = on_message
IOT.ClientId = "put your client id here"
IOT.ClientKey = "put your client key here"
IOT.DeviceId = "put your device id here"

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Name, "put your description here", False, "bool")
IOT.addAsset(Out1Name, "put your description here", True, "bool")
IOT.subscribe()                                        		#starts the bi-directional communication

nextVal = True;
#main loop: run as long as the device is turned on
while True:
    if nextVal == True:
        print(In1Name + " activated")
        IOT.send("true", In1Name)
        nextVal = False
    else:
        print(In1Name + " deactivated")
        IOT.send("false", In1Name)
        nextVal = True
    sleep(5)