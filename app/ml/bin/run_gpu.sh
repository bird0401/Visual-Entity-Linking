#!/bin/sh

#SBATCH -p p
#SBATCH --gres=gpu:1

srun sh -c "singularity exec --nv ../python_ml.simg python main.py"