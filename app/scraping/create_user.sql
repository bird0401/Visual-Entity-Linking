-- command to execute this file
-- mysql -p < create_user.sql

-- Define $MYSQL_ROOT_PASSWORD previously
CREATE USER 'scraper' IDENTIFIED BY "$MYSQL_ROOT_PASSWORD";
GRANT ALL ON *.* TO 'scraper';