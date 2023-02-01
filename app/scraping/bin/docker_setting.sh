#!/bin/sh

sudo docker network create scraping
sudo docker volume create dog_breeds_by_name_db
sudo docker compose up -d
sudo docker exec -it ${id} bash