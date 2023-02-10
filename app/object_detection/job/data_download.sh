#!/bin/sh -l

#PJM -L rscgrp=short-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/object_detection \
    --nv /$HOME/Instance_level_recognition/app/object_detection/gc_cli_latest.sif \
    gsutil -m cp -r gs://data_bird/ .
    # gsutil -m cp -r gs://data_aircraft/ .
    # gsutil -m cp -r gs://data_athlete/ .
    # gsutil -m cp -r gs://data_bread/ .
    # gsutil -m cp -r gs://data_car/ .
    # gsutil -m cp -r gs://data_director/ .
    # gsutil -m cp -r gs://data_us_politician/ .
    # gsutil -m cp -r gs://entity_dogs/ ./
