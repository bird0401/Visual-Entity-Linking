#!/bin/sh

gsutil mb -b on -l us-central1 gs://entity_dogs/
gsutil cp -m -r ../data/imgs gs://entity_dogs/