#!/bin/sh

backup_dir_path='/backup/mysql'
today=$(date +%y%m%d)
password=$mysql_root_password

# create backup file 
mysqldump --opt --all-databases --events --default-character-set=binary -uroot --password=$password 
| gzip > $dirpath/$today.sql.gz

# # delete old file
# expire_period=7
# target_date=$(date --date "$expire_period days ago" +%y%m%d)
# rm -f $backup_dir_path/$target_date.sql.gz