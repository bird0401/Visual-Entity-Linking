#!bin/sh

# Interactive
pjsub --interact -j -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity
module load singularity/3.7.3

# GCS
singularity shell --pwd /$HOME/Instance_level_recognition/app/object_detection $HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif
gsutil -m cp -r gs://entity_dogs/ ./

gcloud auth login
gcloud config set project $PROJECT_ID

# Object Detection
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/object_detection/object_detection_latest.sif

# ML
singularity shell --pwd $HOME/Instance_level_recognition/app/ml/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 

python ./4_ml_test.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 model.weight_file=227-19322/
Loss1.4361_epoch9.bin
Loss1.0723_epoch15.bin
Loss0.7116_epoch21.bin

python ./4_ml_test.py data.category=bird data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3  model.weight_file=227-205450/
Loss0.8952_epoch3.bin
Loss0.7663_epoch4.bin

python ./4_ml_test.py data.category=bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 model.weight_file=

python ./4_ml_test.py data.category=car data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-3 model.weight_file=

python ./4_ml_test.py data.category=director data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 model.weight_file=

python ./4_ml_test.py data.category=dog data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 model.weight_file=

python ./4_ml_test.py data.category=us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 model.weight_file=

