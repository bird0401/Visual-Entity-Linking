#!/bin/sh -l

#PJM -L rscgrp=short-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -L elapse=2:00:00
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Visual-Entity-Linking/app/ml/src/ \
    --nv /$HOME/Visual-Entity-Linking/app/ml/python_ml_latest.sif \
    bash test.sh

    # python ./4_ml.py data.category=aircraft data.data_dir=../../../data/aircraft data.batch_size.train=32 data.batch_size.val=32 optimizer.learning_rate=1e-4
    
