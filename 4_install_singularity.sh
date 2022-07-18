#!/bin/sh

sudo apt-get update && sudo apt-get -y install python dh-autoreconf build-essential libarchive-dev

sudo git clone https://github.com/sylabs/singularity.git
cd singularity
sudo git fetch --all
# sudo git tag -l
sudo git checkout 2.5.2
sudo ./autogen.sh
sudo ./configure --prefix=/usr/local --sysconfdir=/etc
sudo make
sudo make install
