#!/bin/sh

export PROJECT=$(gcloud config list project --format "value(core.project)")
docker build . -t "asia.gcr.io/${PROJECT}/pytorch-custom:latest"
docker push "asia.gcr.io/${PROJECT}/pytorch-custom:latest"