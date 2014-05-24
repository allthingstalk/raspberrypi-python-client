# -*- coding: utf-8 -*-

import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app


In1Name = "button1"                                #name of the button
Out1Name = "led1"


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
IOT.ClientId = "52ed3f2b56644370f0129c97"
IOT.ClientKey = "cvsptzspc5n"
IOT.DeviceId = "5370795d552e1345a02c5cbb"

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Name, "a push button", False, "bool")
IOT.addAsset(Out1Name, "a led", True, "bool")
IOT.subscribe()                                        #starts the bi-directional communication

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