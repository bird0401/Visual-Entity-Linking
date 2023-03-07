-- command to execute this file
-- mysql -p < create_user.sql


CREATE USER 'scraper' IDENTIFIED BY "$MYSQL_ROOT_PASSWORD";
GRANT ALL ON *.* TO 'scraper';