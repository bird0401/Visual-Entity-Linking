-- CREATE DATABASE scraping_dog_breeds_by_name CHARACTER SET utf8;
-- USE scraping_dog_breeds_by_name;

CREATE DATABASE scraping_People_by_name CHARACTER SET utf8;
USE scraping_People_by_name;

CREATE TABLE names(
    wikidata_id CHAR(20) NOT NULL PRIMARY KEY,
    name VARCHAR(200) CHARACTER SET utf8 NOT NULL 
);

CREATE TABLE img_urls (
    img_id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    wikidata_id CHAR(20) NOT NULL,
    img_url VARCHAR(2048) CHARACTER SET utf8 NOT NULL
);

CREATE TABLE img_wikidata_id (
    img_id MEDIUMINT NOT NULL,
    wikidata_id CHAR(20) NOT NULL,
    PRIMARY KEY(img_id, wikidata_id),
    FOREIGN KEY(img_id) 
        REFERENCES img_urls(img_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(wikidata_id) 
        REFERENCES names(wikidata_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE img_path (
    img_id MEDIUMINT NOT NULL PRIMARY KEY,
    path VARCHAR(50) NOT NULL,
    FOREIGN KEY(img_id) 
        REFERENCES img_urls(img_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE USER 'scraper' IDENTIFIED BY "$MYSQL_ROOT_PASSWORD";
GRANT ALL ON *.* TO 'scraper';