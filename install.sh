#!/bin/sh

sudo apt install python3-pip
python3 -m ensurepip
python3 -m pip install -r requirements.txt --upgrade

mkdir temp
cd temp
wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz
rm geckodriver.log
tar -xvzf geckodriver*
sudo chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
cd ..
rm -rf temp