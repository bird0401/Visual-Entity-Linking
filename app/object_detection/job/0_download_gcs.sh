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
# - us_politician_second
# - us_politician_third

category=us_politician
module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/object_detection \
    --nv /$HOME/Instance_level_recognition/app/object_detection/gc_cli_latest.sif \
    gsutil -m cp -r gs://entity_dogs/ .


# gsutil -m cp -r gs://data_${category}/ .
