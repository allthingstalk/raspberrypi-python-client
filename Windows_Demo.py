# -*- coding: utf-8 -*-

#important: before running this demo, make certain that you import the library
#'paho.mqtt.client' into python (https://pypi.python.org/pypi/paho-mqtt)

import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app

#set up the ATT internet of things platform
IOT.DeviceId = "YourDeviceIdHere"
IOT.ClientId = "YourClientIdHere"
IOT.ClientKey = "YourClientKeyHere"

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

nextVal = True;
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
