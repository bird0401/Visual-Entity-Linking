#!/bin/sh

# mysql -p < create_user.sql
mysql -p < create_db_tables.sql

# alter table img_path change path path VARCHAR(100) NOT NULL;