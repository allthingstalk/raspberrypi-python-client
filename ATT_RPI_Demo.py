# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO                            #provides pin support
import ATT_IOT as IOT                              #provide cloud support
from time import sleep                             #pause the app


In1Name = "button1"                                #name of the button
In1Prev = False                                    #previous value of the button
In1Pin = 23

Out1Name = "led1"
Out1Pin = 24

#setup GPIO using Board numbering
#alternative:  GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

#set up the pins
GPIO.setup(In1Pin, GPIO.OUT)
GPIO.setup(Out1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #, pull_up_down=GPIO.PUD_DOWN

#callback: handles values sent from the cloudapp to the device
def on_message(actuatorName, value):
    if actuatorName == Out1Name:
        value = value.lower()                        #make certain that the value is in lower case, for 'True' vs 'true'
        if value == "true":
            GPIO.output(Out1Pin, True)
            IOT.send("true", Out1Name)                #provide feedback to the cloud that the operation was succesful
        elif value == "false":
            GPIO.output(Out1Pin, False)
            IOT.send("false", Out1Name)                #provide feedback to the cloud that the operation was succesful
        else:
            print("unknown value: " + value)
    else:
        print("unknown actuator: " + actuatorName)

#set up the ATT internet of things platform
IOT.on_message = on_message
IOT.ClientId = "put your client id here"
IOT.ClientKey = "put your client id here"
IOT.DeviceId = "put your device id here"

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.addAsset(In1Name, "a push button", False, "bool")
IOT.addAsset(Out1Name, "a led", True, "bool")
IOT.subscribe("Put the mac address here")              #starts the bi-directional communication

#main loop: run as long as the device is turned on
while True:
    if GPIO.input(In1Pin) == 0:                        #for PUD_DOWN, == 1
        if In1Prev == False:
            print(In1Name + " activated")
            IOT.send("true", In1Name)
            In1Prev = True
    elif In1Prev == True:
        print(In1Name + " deactivated")
        IOT.send("false", In1Name)
        In1Prev = False
    sleep(1)