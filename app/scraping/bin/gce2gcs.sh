#!/bin/sh

# $1 is google storage name
# $2 is gce data directory name

# for copy imgs from gce to gcs
gsutil mb -b on -l us-central1 gs://entity_dogs/
gsutil cp -m -r ../data/imgs gs://entity_dogs/
# gsutil mb -b on -l asia-northeast1 gs://$1/
# gsutil cp -m -r ../data/$2 gs://$1/

# for copy csv from gce to gcs
# gsutil mb -b on -l asia-northeast1 gs://mysql_table_csv_9287/
# gsutil cp -r ../data/csv gs://mysql_table_csv_9287/