#!/bin/sh

sudo git clone https://github.com/sylabs/singularity.git
cd singularity
sudo git fetch --all
sudo git checkout 2.5.0
sudo ./autogen.sh
sudo ./configure --prefix=/usr/local
make
sudo make install
