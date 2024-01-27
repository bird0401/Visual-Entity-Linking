#!bin/sh

# Interactive
pjsub --interact -j -o interactive.out -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity

# ML
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/ml/src/ --nv $HOME/Visual-Entity-Linking/app/ml/python_ml_latest.sif 
singularity shell --pwd $HOME/Visual_Entity_Linking/app/gpt --nv $HOME/prophet/python_ml_latest.sif 
singularity shell --pwd $HOME/prophet/ --nv $HOME/prophet/python_ml_latest.sif 

# Object Detection
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/object_detection/src/ --nv $HOME/Visual-Entity-Linking/app/object_detection/object_detection_latest.sif
singularity shell --pwd $HOME/Visual-Entity-Linking/app/object_detection/src/ --nv $HOME/Visual-Entity-Linking/app/ml/python_ml_latest.sif 

# Scraping
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/scraping/src/ --nv $HOME/Visual-Entity-Linking/app/scraping/scraping_latest.sif

# GPT
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/experiment/src --nv $HOME/Visual-Entity-Linking/app/experiment/gpt3_generation_latest.sif

# BEM
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/experiment/src --nv $HOME/Visual-Entity-Linking/app/experiment/tensorflow.sif

# multimodal CLIP
singularity shell --pwd $HOME/CLIP --nv $HOME/CLIP/python_clip_v2_latest.sif
# singularity shell --pwd $HOME/CLIP --nv $HOME/CLIP/python_multimodal_latest.sif

# Scraping
module load singularity/3.7.3
singularity shell --pwd $HOME/Visual-Entity-Linking/app/scraping/src/ --nv $HOME/Visual-Entity-Linking/app/scraping/scraping_latest.sif



# For train
python ./4_ml.py data.category=athlete data.data_dir=../../../data/clean/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4
python ./4_ml.py data.category=athlete data.data_dir=../../../data/origin/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4
# For test
python ./4_ml.py data.category=aircraft data.data_dir=../../../data/origin/aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0325-132028/Loss2.8200_epoch10.bin
python ./4_ml.py data.category=athlete data.data_dir=../../../data/origin/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 general.is_train=False +model.weight_file=0325-131401/Loss1.7903_epoch10.bin
python ./4_ml.py data.category=bird data.data_dir=../../../data/origin/bird data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0325-132030/Loss0.9974_epoch10.bin
python ./4_ml.py data.category=bread data.data_dir=../../../data/origin/bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0325-132028/Loss2.47pip install openai58_epoch9.bin
python ./4_ml.py data.category=car data.data_dir=../../../data/origin/car data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0325-132029/Loss1.3950_epoch9.bin
python ./4_ml.py data.category=director data.data_dir=../../../data/origin/director data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0325-132029/Loss3.5289_epoch10.bin
python ./4_ml.py data.category=dog data.data_dir=../../../data/origin/dog data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0325-132028/Loss1.8206_epoch8.bin
python ./4_ml.py data.category=us_politician data.data_dir=../../../data/origin/us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0325-132036/Loss5.5134_epoch3.bin

# GCS
singularity shell --pwd /$HOME/Instance_level_recognition/app/object_detection $HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif
gsutil -m cp -r gs://entity_dogs/ ./

gcloud auth login
gcloud config set project $PROJECT_ID
