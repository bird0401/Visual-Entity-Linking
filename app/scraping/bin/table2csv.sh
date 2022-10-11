#!/bin/bash

# should pass host environment variable like this
# sudo MYSQL_PASS=$MYSQL_PASS sh ./table2csv.sh 

CONTAINER_ID="b4ef6fed4c41" # db container

sudo rm -rf csv

sudo docker exec db3 bash -c "rm -r /tmp/csv"
sudo docker exec db3 bash -c "mkdir /tmp/csv"
sudo docker exec db3 bash -c "chmod 777 /tmp/csv"

# use multiple -e on purpose instead of one -e because it is easier to read
sudo docker exec db3 mysql -p${MYSQL_PASS} \
    -e "USE scraping_dog_breeds_by_name;" \
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

sudo docker cp ${CONTAINER_ID}:/tmp/csv . \ 
&& sudo chmod 755 ./csv \ # csv directory from container is more strictful
&& sudo rm -r ../data/csv \ 
&& sudo mv ./csv ../data
 