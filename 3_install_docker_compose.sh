#!bin.sh

sudo apt-get update
sudo apt-get install docker-compose-plugin
sudo apt-get install docker-compose-plugin=2.3.3~debian-bullseye
docker compose version