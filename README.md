raspberrypi-python-client
==========

libraries that provide access to the ATT IOT platform, for the Python language (geared for RPI development).

Check the wiki pages for [how-to's & API documentation](https://github.com/allthingstalk/raspberrypi-python-client/wiki).

<!--

### flavours
There are 2 flavours of the IOT library. Use a library according to your needs.
  1. regular: The RPI will act as a single device, directly connected to the IOT platform. You are responsible for creating the device manually on the platform, any assets can be created through the script.
  2. gateway: The RPI will function as a gateway for other devices, which communicate with the gateway-RPI through xbee modules. Devices and their assets are automatically created whenever a new xbee device connects to the gateway.

-->

### Dependencies
  1. all libraries depend on the [paho.mqtt.client module] (http://eclipse.org/paho/clients/python/).
  
<!--

  2. the demo template script for the gateway also relies on:
    - [pyserial] (http://pyserial.sourceforge.net/)
	- [python-xbee] (https://code.google.com/p/python-xbee/)

-->

### Installation
Check out [dexter industries (makers of the GrovePi)](http://www.dexterindustries.com/GrovePi/) excellent [tutorial for the RPI B+](http://www.dexterindustries.com/GrovePi/get-started-with-the-grovepi/raspberry-pi-model-b-grovepi/) on how to install the hardware.  
With this [short tutorial](https://github.com/allthingstalk/gif_python/wiki/Quick-setup-guide), you can set up your Grove Pi and have a script running in a few easy steps. 

[Breadboard GPIO 10 Step Guide] (https://sites.google.com/a/allthingstalk.com/smart-living-help-center/quick-start-with-raspberry-pi-breadboard-gpio-smartliving)

[Noobie Guide] (https://sites.google.com/a/allthingstalk.com/smart-living-help-center/raspberry-pi-smartliving)
