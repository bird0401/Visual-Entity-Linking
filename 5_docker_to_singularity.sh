#!/bin/sh

# $1:image_id, $2:user_name, $3:image_name, $4:tag

sudo docker login
sudo docker tag $1 $2/$3:$4
sudo docker push $2/$3:$4

sudo apt-get install squashfs-tools
sudo singularity pull docker://mot1536/docker-python_python3
