#!/bin/sh -l

#PJM -L rscgrp=share
#PJM -L gpu=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/ml/src/ \
    --nv /$HOME/Instance_level_recognition/app/ml/python_ml_latest.sif \
    python ./4_ml.py data.category=car data.data_dir=../../../data/origin/car data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=1e-3 general.is_train=False +model.weight_file=0325-132029/Loss1.3950_epoch9.bin

