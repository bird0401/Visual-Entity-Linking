#!bin/sh


# IST-CLUSTER

# $2: name of shellscript
# $3: job number

# export PATH=/home/app/singularity/bin:$PATH
# sbatch ../bin/$2.sh
# cat slurm-$3.outsqueue
# squeue


# WISTERIA

# pjsub --interact -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity
# module load singularity/3.7.3

# singularity shell gc_cli_latest.sif 
# cd Instance_level_recognition/app/ml/
# gcloud auth login
# gcloud config set project $PROJECT_ID
# gsutil -m cp -r gs://entity_dogs_debug .
# mv entity_dogs_debug/ data/

# singularity shell /$HOME/Instance_level_recognition/app/ml/python_ml_latest.sif 
# cd Instance_level_recognition/app/ml/src/
# python main.py
pjsub run.sh