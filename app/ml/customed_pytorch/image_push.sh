#!/bin/sh

export PROJECT=$(gcloud config list project --format "value(core.project)")
sudo docker build . -t "asia.gcr.io/${PROJECT}/pytorch-custom:latest"
sudo docker push "asia.gcr.io/${PROJECT}/pytorch-custom:latest"