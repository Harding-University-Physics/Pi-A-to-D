#!/bin/bash
# This is a consolidated version of the Manufacturer's User Guide (see link below)
# https://www.waveshare.com/wiki/High-Precision_AD/DA_Board
# This assumes the user has already edited the Raspberry Pi SPI Config discussed in the
#   "Open SPI Interface" section of the guide.
# That is, this script picks up at the "Install Libraries" section
# This script ends at the AD Demo section


# Run from Downloads Directory
cd $HOME/Downloads


# Install BCM2835 Library
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.68.tar.gz
tar zxvf bcm2835-1.68.tar.gz
cd bcm2835-1.68/
sudo ./configure && sudo make && sudo make check && sudo make install
cd ..


# Wiring Pi
# sudo apt-get install wiringpi  # Not needed for our Pi's
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
cd ..


# Update Python Libraries
sudo apt-get update
sudo apt-get install ttf-wqy-zenhei
sudo apt-get install python-pip
sudo pip install RPi.GPIO
sudo pip install spidev


# Download the Demos
sudo apt-get install p7zip-full
wget https://www.waveshare.com/w/upload/5/5e/High-Precision-AD-DA-Board-Code.7z
7z x High-Precision-AD-DA-Board-Code.7z -r -o./High-Precision-AD-DA-Board-Code
