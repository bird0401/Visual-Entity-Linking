#!/bin/sh -l

#PJM -L rscgrp=debug-a
#PJM -L node=1
#PJM -L elapse=0:30:00
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/ml/src/ \
    --nv /$HOME/Instance_level_recognition/app/ml/python_ml_latest.sif \
    python ./main.py