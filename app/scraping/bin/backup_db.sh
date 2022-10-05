#!/bin/sh

sudo docker run --rm \
--mount type=volume,src=dog_breeds_by_name_db,dst=/backup_target \
--mount type=bind,src="$PWD",dst=/bind_dir \
busybox tar czf /bind_dir/backup/db_backup.tar.gz -C /backup_target .