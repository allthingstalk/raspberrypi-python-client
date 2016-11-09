sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo pip install RPi.GPIO
cd /home/pi/raspberrypi-python-client	#make certain that git clone is done frmo the right directory.
sudo pip install paho-mqtt
sudo pip install att-iot-client
git clone https://github.com/DexterInd/GrovePi 	
sudo cp GrovePi/Software/Python/grovepi.py examples
sudo cp GrovePi/Software/Python/grovepi.py experiments
cd GrovePi/Script
sudo chmod +x install.sh
sudo ./install.sh
