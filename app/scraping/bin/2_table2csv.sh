#!/bin/bash

# You should pass host environment variable like this
# sudo MYSQL_PASS=$MYSQL_PASS sh ./2_table2csv.sh data_aircraft

# change by each category
# - CONTAINER_ID
# - data_dir: e.g. data_aircraft
# - USE ${database name} 

# list of data directory and database name 
# scraping_dog_breeds_by_name, data_dog
# Aircraft_by_popular_name, data_aircraft
# Automobiles_by_brand_by_model, data_car
# Breads_by_name, data_bread
# Film_directors_by_name, data_
# Gallery_pages_of_birds, data_bird
# Politicians_of_the_United_States_by_name, data_
# Sportspeople_by_name, data_

CONTAINER_ID="2b94422639b4" # db container
data_dir=data_bird

sudo rm -r csv
sudo docker exec db3 bash -c "rm -r /tmp/csv"
sudo docker exec db3 bash -c "mkdir /tmp/csv"
sudo docker exec db3 bash -c "chmod 777 /tmp/csv"

# use multiple -e on purpose instead of one -e because it is easier to read
sudo docker exec db3 mysql -p${MYSQL_PASS} \
    -e "USE Gallery_pages_of_birds;" \
    -e "SELECT 'wikidata_id', 'name' 
        UNION SELECT * FROM names INTO OUTFILE '/tmp/csv/names.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" \
    -e "SELECT 'img_id', 'wikidata_id', 'img_url' 
        UNION SELECT * FROM img_urls INTO OUTFILE '/tmp/csv/img_urls.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" \
    -e "SELECT 'img_id', 'wikidata_id' 
        UNION SELECT * FROM img_wikidata_id INTO OUTFILE '/tmp/csv/img_wikidata_id.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" \
    -e "SELECT 'img_id', 'path' 
        UNION SELECT * FROM img_path INTO OUTFILE '/tmp/csv/img_path.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" 

sudo docker cp ${CONTAINER_ID}:/tmp/csv . 
sudo chmod 755 ./csv 
sudo rm -r ../${data_dir}/csv
sudo mv ./csv ../${data_dir}
