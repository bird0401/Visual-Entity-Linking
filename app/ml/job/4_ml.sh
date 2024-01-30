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
    python ./4_ml.py data.category= data.batch_size.train= data.batch_size.val= optimizer.learning_rate= data.data_dir=
    # For test
    # python ./4_ml.py data.category= data.batch_size.train= data.batch_size.val= optimizer.learning_rate= data.data_dir= general.is_train=False +model.weight_file=

    # currenct parameters
    # python ./4_ml.py data.category=aircraft data.data_dir=../../../data/aircraft data.batch_size.train=32 data.batch_size.val=32 optimizer.learning_rate=1e-4 train.top_k=20