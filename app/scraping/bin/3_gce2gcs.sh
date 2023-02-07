#!/bin/sh
# copy imgs from gce to gcs
# sh ./3_gce2gcs.sh  

# list of data directory
# data_aircraft
# data_bird
# data_bread
# data_car
# data_dog
data_dir=$1
# data_dir="data_bread"

# for data directory (images and csv)
gsutil mb -b on -l asia-northeast1 gs://${data_dir}
gsutil -m cp -r ../${data_dir}/* gs://${data_dir} 