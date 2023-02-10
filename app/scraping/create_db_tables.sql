-- command to execute this file
-- mysql -p < create_db_tables.sql


-- CREATE DATABASE scraping_dog_breeds_by_name CHARACTER SET utf8;
-- USE scraping_dog_breeds_by_name;

-- CREATE DATABASE scraping_People_by_name CHARACTER SET utf8;
-- USE scraping_People_by_name;

-- CREATE DATABASE Automobiles_by_brand_by_model CHARACTER SET utf8;
-- USE Automobiles_by_brand_by_model;

-- CREATE DATABASE Aircraft_by_popular_name CHARACTER SET utf8;
-- USE Aircraft_by_popular_name;

-- CREATE DATABASE Breads_by_name CHARACTER SET utf8;
-- USE Breads_by_name;

-- CREATE DATABASE Gallery_pages_of_birds CHARACTER SET utf8;
-- USE Gallery_pages_of_birds;

-- CREATE DATABASE Politicians_of_the_United_States_by_name CHARACTER SET utf8;
-- USE Politicians_of_the_United_States_by_name;

-- CREATE DATABASE Sportspeople_by_name CHARACTER SET utf8;
-- USE Sportspeople_by_name;

CREATE DATABASE Film_directors_by_name CHARACTER SET utf8;
USE Film_directors_by_name;


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
    path VARCHAR(100) NOT NULL,
    FOREIGN KEY(img_id) 
        REFERENCES img_urls(img_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
