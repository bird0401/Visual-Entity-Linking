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