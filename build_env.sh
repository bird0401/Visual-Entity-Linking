#!/bin/sh

cd docker-python/
docker compose up -d --build
docker compose exec python3 bash
python --version
