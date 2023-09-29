#!/bin/sh -l

#PJM -L rscgrp=share
#PJM -L gpu=1
#PJM -L jobenv=singularity
#PJM -L elapse=24:00:00
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Visual-Entity-Linking/app/scraping/src/ \
    --nv /$HOME/Visual-Entity-Linking/app/scraping/scraping_latest.sif \
    python extract_entity_name_from_id.py