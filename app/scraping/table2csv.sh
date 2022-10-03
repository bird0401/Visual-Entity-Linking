#!/bin/bash

# should pass host environment variable like this
# sudo MYSQL_PASS=$MYSQL_PASS sh ./table2csv.sh 

sudo rm -rf csv

sudo docker exec db3 bash -c "rm -r /tmp/csv"
sudo docker exec db3 bash -c "mkdir /tmp/csv"
sudo docker exec db3 bash -c "chmod 777 /tmp/csv"

sudo docker exec db3 mysql -p${MYSQL_PASS} \
    -e "USE scraping_dog_breeds_by_name;" \
    -e "SELECT 'id', 'path' 
        UNION SELECT * FROM img_path INTO OUTFILE '/tmp/csv/img_path.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" \
    -e "SELECT 'id', 'name' 
        UNION SELECT * FROM names INTO OUTFILE '/tmp/csv/names.csv' 
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';"
sudo docker cp b4ef6fed4c41:/tmp/csv . \
&& sudo chmod 755 csv
