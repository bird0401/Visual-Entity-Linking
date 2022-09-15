import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
import re
import os
import shutil
from fake_useragent import UserAgent
import pathlib
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import traceback    
import mysql.connector
import sys

# args = sys.argv

mysql_user = 'scraper'
mysql_password = os.environ['MYSQL_PASS']
host = 'db1'
database = 'scraping_dog_breeds_by_name'

connection = mysql.connector.connect(
    user=mysql_user,
    password=mysql_password,
    host = host,
    database=database,
    port=3306
    )

cur = connection.cursor(buffered=True)

insert_new_name = (
  "INSERT INTO names (wikidata_id, name) "
  "VALUES(%s, %s)")

insert_new_img_url = (
  "INSERT INTO img_urls (img_url) "
  "VALUE(%s)")

insert_new_img_wikidata_id = (
  "INSERT INTO img_wikidata_id (img_id, wikidata_id) "
  "VALUES(%s, %s)")

insert_new_img_path = (
  "INSERT INTO img_path (img_id, path) "
  "VALUES(%s, %s)")

# img_urls_in_db = cur.execute("SELECT img_url FROM img_urls")
cur.execute("SELECT img_url FROM img_urls")
img_urls_in_db = cur.fetchall()
# wikidata_ids_in_db = cur.execute("SELECT wikidata_id FROM names")
cur.execute("SELECT wikidata_id FROM names")
wikidata_ids_in_db = cur.fetchall()

# wikidata_id = 'hiro'
# entity_name = 'matsu'
# file_path = '/re'
# for url in ['i', 'j', 'k', 'l', 'm']:
#     cur.execute(insert_new_img_url, (url,))
#     img_id = cur.lastrowid
#     cur.execute(insert_new_name, (wikidata_id+str(img_id), entity_name+str(img_id)))
#     cur.execute(insert_new_img_wikidata_id, (img_id, wikidata_id+str(img_id)))
#     cur.execute(insert_new_img_path, (img_id, file_path))
#     connection.commit()

for img_url in img_urls_in_db:
  print(img_url)
print()
for wikidata_id in wikidata_ids_in_db:
  print(wikidata_id)

connection.close()