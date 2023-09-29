#!/bin/sh

sudo apt-get install squashfs-tools
singularity pull --docker-login docker://mot1536/gpt3_generation
singularity shell experiment.simg
