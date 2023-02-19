#!/bin/sh -l

#PJM -L rscgrp=short-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

# List of categories
# - aircraft
# - athlete
# - bird
# - bread
# - car
# - director
# - dogs
# - us_politician

category=director
module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/object_detection \
    --nv /$HOME/Instance_level_recognition/app/object_detection/gc_cli_latest.sif \
    gsutil -m cp -r gs://data_${category}/ .
