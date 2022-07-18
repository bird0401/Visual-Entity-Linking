
#!/bin/sh

git clone https://github.com/sylabs/singularity.git

cd singularity

git fetch --all

git checkout 2.5.0

./autogen.sh

./configure --prefix=/usr/local

make

sudo make install
