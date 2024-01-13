.PHONY: up format migrate batch runserver down

IMAGE_NAME=gr

interact:
	pjsub --interact -j -o interactive.out -g gk77 -L rscgrp=interactive-a,node=1,jobenv=singularity
up:
	docker compose up -d

format:
	docker run -it -v $(PWD):/app $(IMAGE_NAME) black /app
	docker run -it -v $(PWD):/app $(IMAGE_NAME) isort /app

migrate:
	docker exec -it $(IMAGE_NAME) python django_rest_framework/manage.py makemigrations
	docker exec -it $(IMAGE_NAME) python django_rest_framework/manage.py migrate

batch: 
	docker exec -it $(IMAGE_NAME) python django_rest_framework/manage.py batch_process 

# サーバー起動用だが、現状はAPIが外部から呼び出されることはないので利用する予定はない
runserver:
	docker exec -it $(IMAGE_NAME) python django_rest_framework/manage.py runserver 0.0.0.0:8503

down:
	docker compose down
