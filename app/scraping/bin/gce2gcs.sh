#!/bin/sh

gsutil mb -b on -l us-central1 gs://entity_dogs/
gsutil -m cp -r ../data/imgs gs://entity_dogs/