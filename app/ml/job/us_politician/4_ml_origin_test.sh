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
    python ./4_ml.py data.category=us_politician data.data_dir=../../../data/origin/us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0325-132036/Loss5.5134_epoch3.bin
