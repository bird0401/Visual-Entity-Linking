#!bin/sh


# IST-CLUSTER

# $2: name of shellscript
# $3: job number

# export PATH=/home/app/singularity/bin:$PATH
# sbatch ../bin/$2.sh
# cat slurm-$3.outsqueue
# squeue


# WISTERIA

pjsub --interact -j -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity
module load singularity/3.7.3

# For gcs to server
singularity shell gc_cli_latest.sif 
cd Instance_level_recognition/app/ml/
gcloud auth login
gcloud config set project $PROJECT_ID
gsutil -m cp -r gs://entity_dogs_debug .
mv entity_dogs_debug/ data/

singularity shell --pwd /$HOME/Instance_level_recognition/app/ml/src $HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif
singularity shell --pwd /$HOME/Instance_level_recognition/app/object_detection/src $HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif
gsutil -m cp -r gs://entity_dogs_debug_crop/ ./
gsutil -m cp -r gs://entity_dogs/ ./
gsutil -m cp -r ./ gs://entity_dogs_debug_crop/

# For object detection
singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 
python 1_preprocess.py
python 2_main.py

singularity shell --pwd $HOME/Instance_level_recognition/app/object_detection/src/ --nv $HOME/Instance_level_recognition/app/object_detection/object_detection_latest.sif
python main.py

# For ML
singularity shell --pwd $HOME/Instance_level_recognition/app/ml/src/ --nv $HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 
python 1_create_df.py 
python 2_main.py

pjsub /$HOME/Instance_level_recognition/app/ml/job/run.sh
pjsub /$HOME/Instance_level_recognition/app/object_detection/job/preprocess.sh
pjsub /$HOME/Instance_level_recognition/app/object_detection/job/data_download.sh


