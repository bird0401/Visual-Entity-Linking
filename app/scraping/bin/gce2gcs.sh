#!/bin/sh
# copy imgs from gce to gcs
# $1 is google storage name
# $2 is gce data directory name

# for imgs
# gsutil mb -b on -l asia-northeast1 gs://$1/
# gsutil cp -m -r ../data/$2 gs://$1/

# for csv
gsutil rm -r gs://mysql_table_csv_9287/
gsutil mb -b on -l asia-northeast1 gs://mysql_table_csv_9287/
gsutil cp -r ../data/csv gs://mysql_table_csv_9287/