sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo pip install RPi.GPIO
cd /home/pi/raspberrypi-python-client	#make certain that git clone is done frmo the right directory.
sudo pip install paho-mqtt
git clone https://github.com/DexterInd/GrovePi 	
sudo cp /home/pi/raspberrypi-python-client/GrovePi/Software/Python/grovepi.py /home/pi/raspberrypi-python-client
sudo cp /home/pi/raspberrypi-python-client/GrovePi/Software/Python/grovepi.py /home/pi/raspberrypi-python-client/examples
sudo cp /home/pi/raspberrypi-python-client/ATT_IOT.py /home/pi/raspberrypi-python-client/examples
cd GrovePi/Script
sudo chmod +x install.sh
sudo ./install.sh
