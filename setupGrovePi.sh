sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo easy_install -U distribute
git clone https://github.com/DexterInd/GrovePi 
cd GrovePi/Script
sudo chmod +x install.sh
sudo ./install.sh
cd ..
cd ..
sudo pip install RPi.GPIO
sudo pip install paho-mqtt
