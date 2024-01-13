#!/bin/sh -l

#PJM -L rscgrp=regular-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -L elapse=8:00:00
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Visual-Entity-Linking/app/object_detection/src/ \
    --nv /$HOME/Visual-Entity-Linking/app/object_detection/object_detection_latest.sif \
    python ./2_detect.py director
