#!/usr/bin/python

# not yet supported

import serial
from xbee import ZigBee
import allthingstalk_python_gateway_lib as IOT                              #provide cloud support

#set up the ATT internet of things platform
IOT.ClientId = "YourClientId"
IOT.ClientKey = "YourClientKey"

#serial_port = serial.Serial('/dev/ttyUSB0', 9600)        #for linux
serial_port = serial.Serial('COM5', 9600)                 #for windows
zb = ZigBee(serial_port)

#callback: handles values sent from the cloudapp to the device
def on_message(actuatorName, value):
    print "not yet supported"
IOT.on_message = on_message

#make certain that the device & it's features are defined in the cloudapp
IOT.connect()
IOT.subscribe()                                        #starts the bi-directional communication

devices = []                                           #contains the list of devices already connected to the

while True:
    try:
        data = zb.wait_read_frame() #Get data for later use
        print "found data: "
        print data
        deviceId = data['source_addr_long'].encode("HEX")
        if deviceId not in devices:                     										#if we haven't seen this deviceId yet, check if we need to create a new device for it
            devices.append(deviceId)
            print "Check if device already known in IOT"
            if IOT.deviceExists(deviceId) == False:     										#as we only keep deviceId's locally in memory, it could be that we already created the device in a previous run. We only want to create it 1 time.
                print "creating new device"
                IOT.addDevice(deviceId, 'name of the device', "description of the device" )		#adjust according to your needs
                IOT.addAsset(1, deviceId, 'asset name', 'asset description', False, 'int')	#adjust according to your needs
                IOT.addAsset(2, deviceId, "asset name", "asset description", False, "int")	#adjust according to your needs
                IOT.addAsset(3, deviceId, "asset name", "asset description", False, "int")	#adjust according to your needs
            else:
                IOT.subscribeDevice(deviceId)
        IOT.send(data['samples'][0]['adc-1'], deviceId, 1)									#adjust according to your needs
        IOT.send(data['samples'][0]['adc-2'], deviceId, 2)									#adjust according to your needs
        IOT.send(data['samples'][0]['adc-3'], deviceId, 3)									#adjust according to your needs
    except KeyboardInterrupt:                                                    				#stop the script
        break
    except ValueError as e:                                                      				#in case of an xbee error: print it and try to continue
        print e

serial_port.close()																				#when done, close serial port	