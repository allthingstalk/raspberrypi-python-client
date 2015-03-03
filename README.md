raspberrypi-python-client
==========

libraries that provide access to the ATT IOT platform, for the Python language (geared for RPI development).

Check the wiki pages for [how-to's & API documentation](https://github.com/allthingstalk/raspberrypi-python-client/wiki).

<!--

### flavours
There are 2 flavours of the IOT library. Use a library according to your needs.
  1. regular: The RPI will act as a single device, directly connected to the IOT platform. You are responsible for creating the device manually on the platform, any assets can be created through the script.
  2. gateway: The RPI will function as a gateway for other devices, which communicate with the gateway-RPI through xbee modules. Devices and their assets are automatically created whenever a new xbee device connects to the gateway.


### Dependencies
  1. The library depend on the [paho.mqtt.client module](http://eclipse.org/paho/clients/python/).
  


  2. the demo template script for the gateway also relies on:
    - [pyserial] (http://pyserial.sourceforge.net/)
	- [python-xbee] (https://code.google.com/p/python-xbee/)

-->

### Installation
- Copy the library to the RPI:
	- Run `git clone https://github.com/allthingstalk/raspberrypi-python-client`
	- or use an ftp client to copy the library to your RPI.
- Run `sudo bash raspberrypi-python-client/setupGrovePi.sh`  in case you have the grovePi shield
or `sudo bash raspberrypi-python-client/setupNoShield.sh` if you don't have a grovePi shield

### Instructions

  1. Setup the raspberry pi hardware
    - Grove kit shield
    - Push button to A2
    - Led light to D4
  2. Create the device in the IOT platform.
  3. Open the 'Shield_Demo.py' template script: `sudo nano Shield_Demo.py`
  3. fill in the missing strings: replace deviceId, clientId, clientKey. Optionally change/add the sensor & actuator names, pins, descriptions, types. 
  4. Run the script: `python Shield_Demo.py`


### Extra info
Check out [dexter industries (makers of the GrovePi)](http://www.dexterindustries.com/GrovePi/) excellent [tutorial for the RPI B+](http://www.dexterindustries.com/GrovePi/get-started-with-the-grovepi/raspberry-pi-model-b-grovepi/) on how to install the hardware.  
With this [short tutorial](https://github.com/allthingstalk/raspberrypi-python-client/wiki/Quick-setup-guide), you can set up your Grove Pi and have a script running in a few easy steps. 
