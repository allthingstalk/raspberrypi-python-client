__author__ = 'Jan Bogaerts'
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

import ATT_IOT as IOT
import datetime
import logging

WatchDogAssetId = -1    #the asset id used by the watchdog. Change this if it interfers with your own asset id's.
PingFrequency = 3000    #the frequency in seconds, that a ping is sent out (and that the system expects a ping back)


_nextPingAt = None      # the moment in time that the next ping should be sent.
_pingCounter = 0        # the count of the ping, increments every time a ping is sent.
_lastReceived = 0       # the ping counter that was last received.

def ping():
    """send a ping to the server"""
    global _nextPingAt
    _nextPingAt = datetime.datetime.now() + datetime.timedelta(0, PingFrequency)
    IOT.sendCommandTo(_pingCounter, IOT.DeviceId, WatchDogAssetId)

def checkPing():
    """check if we need to resend a ping and if we received the previous ping in time"""
    global _pingCounter
    if _nextPingAt <= datetime.datetime.now():
        if _lastReceived != _pingCounter:
            logging.error("ping didn't arrive in time, resetting connection")
            IOT._mqttClient.reconnect()
            return False
        else:
            _pingCounter += 1
            ping()

    return True

def isWatchDog(id, value):
    """check if an incomming command was a ping from the watchdog
    :returns: if the id was that of the watchdog.
    :rtype: bool
    """
    global _lastReceived
    if id == str(WatchDogAssetId):
        _lastReceived = long(value)
        logging.info("received ping: " + str(_lastReceived))
        return True
    return False

def setup():
    IOT.addAsset(WatchDogAssetId, "network watchdog", "used to verify the connectivity with the broker", True, "integer")