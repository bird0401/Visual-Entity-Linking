#!/bin/sh -l

#PJM -L rscgrp=share
#PJM -L gpu=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Visual-Entity-Linking/app/ml/src/ \
    --nv /$HOME/Visual-Entity-Linking/app/ml/python_ml_latest.sif \
    python ./4_ml.py data.category=athlete data.data_dir=../../../data/clean/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4