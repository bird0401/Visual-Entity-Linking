#!/bin/sh -l

#PJM -L rscgrp=share
#PJM -L gpu=1
#PJM -L jobenv=singularity
#PJM -g gk77
#PJM -j

module load singularity/3.7.3
singularity exec \
    --pwd $HOME/Visual-Entity-Linking/app/experiment/src \
    --nv $HOME/Visual-Entity-Linking/app/experiment/gpt3_generation_latest.sif \
    python ./make_qa_file.py bird ans all 
    