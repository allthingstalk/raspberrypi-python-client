# -*- coding: utf-8 -*-
# __author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Production"  # "Development", or "Production"

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

import logging
logging.getLogger().setLevel(logging.INFO)

import att_iot_client.ATT_IOT as IOT               #provide cloud support
import att_iot_client.nw_watchdog as wd
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
    if not wd.isWatchDog(id, value):
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
IOT.connect(secure=True)
wd.setup()                                             #create the assets for the watchdog
IOT.addAsset(In1Id, In1Name, "put your description here", False, "boolean")
IOT.addAsset(Out1Id, Out1Name, "put your description here", True, "boolean")
IOT.subscribe(port=8883, secure=True)                 #starts the bi-directional communication
wd.ping()                                               #send the first ping to start the watchdog process.

nextVal = True
#main loop: run as long as the device is turned on
while True:
    wd.checkPing()
    if nextVal == True:
        print(In1Name + " activated")
        IOT.send("true", In1Id)
        nextVal = False
    else:
        print(In1Name + " deactivated")
        IOT.send("false", In1Id)
        nextVal = True
    sleep(5)