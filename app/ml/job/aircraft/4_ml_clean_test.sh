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
    python ./4_ml.py data.category=aircraft data.data_dir=../../../data/clean/aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 general.is_train=False +model.weight_file=0316-112142/Loss2.5827_epoch10.bin
