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

args = sys.argv
mysql_user, mysql_password = args[1], args[2]
database, host = 'scraping_dog_breeds_by_name', 'localhost'

connection = mysql.connector.connect(
    user=mysql_user,
    password=mysql_password,
    host = host,
    database=database
    )

cur = connection.cursor()

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

# file_path = 'hiro'
for url in ['i', 'j', 'k', 'l', 'm']:
    cur.execute(insert_new_img_url, (url,))
    img_id = cur.execute("SELECT LAST_INSERT_ID();")
    # cur.execute(insert_new_img_wikidata_id, (img_id, wikidata_id))
    # cur.execute(insert_new_img_path, (img_id, file_path))
    connection.commit()
connection.close()