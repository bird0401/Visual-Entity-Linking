#!/bin/sh

#PJM -L rscgrp=debug-a
#PJM -L node=1
#PJM -L elapse=0:15:00
#PJM -L jobenv=singularity
#PJM -g group1
#PJM -j

module load singularity/2.5.2
singularity exec --nv ../python_ml.simg python main.py
