#!/bin/sh

export PROJECT=$(gcloud config list project --format "value(core.project)")
docker build ../ -f Dockerfile -t "gcr.io/${PROJECT}/pytorch-custom:latest"
docker push "gcr.io/${PROJECT}/tf-custom:latest"