#!/bin/sh -l

#PJM -L rscgrp=share
#PJM -L gpu=1
#PJM -L jobenv=singularity
#PJM -L elapse=48:00:00
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Instance_level_recognition/app/scraping/src/ \
    --nv /$HOME/Instance_level_recognition/app/scraping/scraping_latest.sif \
    python extract_wikipedia.py