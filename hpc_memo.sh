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

python ./4_ml_test.py data.category=aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=227-191032/Loss2.5025_epoch11.bin
python ./4_ml_test.py data.category=aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=0228-011349/Loss2.9088_epoch7.bin

python ./4_ml_test.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 +model.weight_file=227-19322/Loss0.7116_epoch21.bin
python ./4_ml_test.py data.category=athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 +model.weight_file=0228-000247/Loss0.7611_epoch16.bin

python ./4_ml_test.py data.category=bird data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3  +model.weight_file=227-205450/Loss0.7663_epoch4.bin
python ./4_ml_test.py data.category=bird data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3  +model.weight_file=0227-225231/Loss0.9829_epoch8.bin

python ./4_ml_test.py data.category=bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 +model.weight_file=0227-225326/Loss2.2433_epoch9.bin
python ./4_ml_test.py data.category=bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 +model.weight_file=0227-225227/Loss2.5168_epoch4.bin

python ./4_ml_test.py data.category=car data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-3 +model.weight_file=227-191033/Loss1.2580_epoch9.bin
python ./4_ml_test.py data.category=car data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-3 +model.weight_file=0228-011619/Loss1.6487_epoch8.bin

python ./4_ml_test.py data.category=director data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 +model.weight_file=0227-234015/Loss2.2752_epoch11.bin
python ./4_ml_test.py data.category=director data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 +model.weight_file=0228-002853/Loss3.4156_epoch7.bin

python ./4_ml_test.py data.category=dog data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=227-191033/Loss1.4483_epoch9.bin
python ./4_ml_test.py data.category=dog data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=0228-180802/Loss1.7115_epoch7.bin

python ./4_ml_test.py data.category=us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=227-19113/Loss3.4866_epoch11.bin
python ./4_ml_test.py data.category=us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 +model.weight_file=0228-011715/Loss4.5115_epoch6.bin

