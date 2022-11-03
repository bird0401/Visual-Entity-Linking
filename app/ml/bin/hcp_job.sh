#!bin/sh

# $2: name of shellscript
# $3: job number

# export PATH=/home/app/singularity/bin:$PATH
# sbatch ../bin/$2.sh
# cat slurm-$3.outsqueue
# squeue

pjsub run.sh