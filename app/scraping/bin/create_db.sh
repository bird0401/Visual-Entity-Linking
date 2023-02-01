#!/bin/sh

mysql -p < create_user.sql
mysql -p < create_db_tables.sql