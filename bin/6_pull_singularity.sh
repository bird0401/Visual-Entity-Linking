#!/bin/sh

sudo apt-get install squashfs-tools
singularity pull docker://mot1536/python_ml
singularity shell python_ml.simg
