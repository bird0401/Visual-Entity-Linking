#!/bin/sh

sudo docker pull gcr.io/google.com/cloudsdktool/google-cloud-cli:latest
sudo docker run --rm gcr.io/google.com/cloudsdktool/google-cloud-cli:latest gcloud version
sudo docker run -it gcr.io/google.com/cloudsdktool/google-cloud-cli:latest bash

# after logging in shell "gcloud auth login"