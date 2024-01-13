#!/bin/sh -l

#PJM -L rscgrp=debug-a
#PJM -L node=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd /$HOME/Visual-Entity-Linking/app/scraping/src/ \
    --nv /$HOME/Visual-Entity-Linking/app/scraping/scraping_latest.sif \
    python make_relations_text.py