#!bin/sh

# Interactive
pjsub --interact -j -o interactive.out -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity
module load singularity/3.7.3

# Object Detection
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/object_detection/object_detection_latest.sif
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 

# ML
module load singularity/3.7.3
singularity shell --pwd $HOME/Instance_level_recognition/app/ml/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 

# For train
python ./4_ml.py data.category=athlete data.data_dir=../../../data/clean/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4
python ./4_ml.py data.category=athlete data.data_dir=../../object_detection/data data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 
# For test
python ./4_ml.py data.category=aircraft data.data_dir=../../../data/clean/aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0316-112142/Loss2.5827_epoch10.bin | tee aircraft.log
python ./4_ml.py data.category=athlete data.data_dir=../../../data/clean/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 general.is_train=False +model.weight_file=0317-234029/Loss1.2481_epoch10.bin | tee athlete.log
python ./4_ml.py data.category=bird data.data_dir=../../../data/clean/bird data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0316-112112/Loss0.7484_epoch6.bin | tee bird.log
python ./4_ml.py data.category=bread data.data_dir=../../../data/clean/bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0316-112111/Loss2.2219_epoch8.bin | tee bread.log
python ./4_ml.py data.category=car data.data_dir=../../../data/clean/car data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0316-112128/Loss1.2356_epoch6.bin | tee car.log
python ./4_ml.py data.category=director data.data_dir=../../../data/clean/director data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0316-112112/Loss2.3195_epoch10.bin | tee director.log
python ./4_ml.py data.category=dog data.data_dir=../../../data/clean/dog data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0316-112147/Loss1.4124_epoch9.bin | tee dog.log
python ./4_ml.py data.category=us_politician data.data_dir=../../../data/clean/us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0318-100458/Loss3.2651_epoch9.bin | tee us_politician.log

# GCS
singularity shell --pwd /$HOME/Instance_level_recognition/app/object_detection $HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif
gsutil -m cp -r gs://entity_dogs/ ./

gcloud auth login
gcloud config set project $PROJECT_ID
