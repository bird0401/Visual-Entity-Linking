#!/bin/sh -l

#PJM -L rscgrp=short-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/ml/ \
    /$HOME/Instance_level_recognition/app/ml/gc_cli_latest.sif \
    gsutil -m cp -r ../object_detection/src/runs/detect gs://entity_dogs_debug_crop/
    # gsutil -m cp -r gs://entity_dogs_debug/ ../object_detection/src/runs/detect

