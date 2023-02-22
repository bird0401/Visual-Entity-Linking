#!/bin/sh -l

#PJM -L rscgrp=short-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/object_detection/src/ \
    --nv /$HOME/Instance_level_recognition/app/object_detection/object_detection_latest.sif \
    python ./1_preprocess_athlete.py
