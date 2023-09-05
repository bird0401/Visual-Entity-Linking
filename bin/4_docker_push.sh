#!/bin/sh

# $1:user_name $2:image_id, $3:tag $4:image_name

sudo docker login
sudo docker tag $2 $1/$4:$3
sudo docker push $1/$4:$3
