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
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/object_detection/object_detection_latest.sif
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 

# ML
singularity shell --pwd $HOME/Instance_level_recognition/app/ml/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 

# For train
python ./2_ml.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 data.data_dir=../../../data/clean general.is_debug=True
python ./2_ml.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 data.data_dir=../../object_detection/data # For origin
# For test
python ./2_ml.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 data.data_dir=../data_clean general.is_train=False +model.weight_file=0304-231755/Loss2.6476_epoch1.bin

