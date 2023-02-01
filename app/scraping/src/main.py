from bs4 import BeautifulSoup
import re
import os
import shutil
import pathlib
import traceback    
import mysql.connector
import sys
from util import *

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')


mysql_user = os.environ['MYSQL_USER']
mysql_password = os.environ['MYSQL_PASS']
host = os.environ['DB_HOST']
database = os.environ['DATABASE']

connection = mysql.connector.connect(
    user=mysql_user,
    password=mysql_password,
    host = host,
    database=database,
    port=3306
    )

cur = connection.cursor()
cur.execute("SELECT wikidata_id, img_url FROM img_urls")
img_urls_in_db = cur.fetchall()
img_urls_in_db = set([(wikidata_id, img_url) for (wikidata_id, img_url) in img_urls_in_db])
cur.execute("SELECT wikidata_id FROM names")
wikidata_ids_in_db = cur.fetchall()
wikidata_ids_in_db = set([wikidata_id for (wikidata_id,) in wikidata_ids_in_db])

def ExtractNextPageURL(url, text="next page"):
  res = Fetch(url)
  soup = BeautifulSoup(res.text, "html.parser")
  try:
    t=soup.find(text=text)
    if t: return ToAbsURL(related_url = t.parent.attrs['href'])
  except Exception: 
    traceback.print_exc()
    return None

def ExtractEntityURLs(category):
  entity_list_page_url=ToAbsURL(related_url = f'/wiki/Category:{category}')

  while entity_list_page_url:
    res = Fetch(entity_list_page_url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    try:
      elems=soup.find_all(class_="CategoryTreeItem")
      for elem in elems:
        entity_name = elem.find('a').text
        entity_url = ToAbsURL(related_url = elem.find('a').attrs['href'])
        if entity_name and entity_url: yield entity_name, entity_url
        else: continue
    except Exception:
      traceback.print_exc()

    entity_list_page_url=ExtractNextPageURL(entity_list_page_url)

def ExtractEntityID(entity_url):
  try: 
    res = Fetch(entity_url)
    soup = BeautifulSoup(res.text, "html.parser") 
    wikidata_url=soup.find(href=re.compile("^https://www.wikidata.org/wiki/Q")).attrs["href"]
    wikidata_id=pathlib.Path(wikidata_url).stem
    return wikidata_id
  except Exception:
    print(f"in {entity_url}")
    traceback.print_exc()
    return None

def MakeEntityImgDir(id):
  img_path = "../data/imgs/" + id
  if not os.path.isdir(img_path): os.makedirs(img_path)
  return img_path

def ExtractImageURL(img_page_url):
      try: 
        res = Fetch(img_page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        l=soup.find(class_="fullImageLink")
        if l: 
          img_url = l.a.attrs['href']
          return img_url
        else: 
          print("can't extract image URL") # for example, in the case that the file is mp3
      except Exception: 
        traceback.print_exc()
        return None

def ExtractImageURLs(entity_img_list_page_url):
  """
  Image Page is the page which contains an image, description, bottons, etc.
  after extract Image Page URL, extract image url from this Page 
  """
  first_page = True
  while entity_img_list_page_url:
    res = Fetch(entity_img_list_page_url)
    soup = BeautifulSoup(res.text, "html.parser")
    try:
      image_classes=soup.find_all(class_="galleryfilename galleryfilename-truncate")
      if first_page and len(image_classes) < 5:
        logger.info(f"{entity_img_list_page_url} has only {len(image_classes)} images")
        return
      for image_class in image_classes:
        img_page_url=ToAbsURL(related_url = image_class.attrs['href'])
        img_url = ExtractImageURL(img_page_url)
        if img_url: yield img_url
        else: continue
    except Exception:
      traceback.print_exc()
    entity_img_list_page_url=ExtractNextPageURL(entity_img_list_page_url)
    first_page = False

def DownloadImage(url, file_path, wikidata_id):
  res=Fetch(url)
  if res: 
    with open(file_path, "wb") as f: f.write(res.content)

    insert_new_img_url = (
      "INSERT INTO img_urls (wikidata_id, img_url) "
      "VALUE (%s, %s)")
    insert_new_img_wikidata_id = (
      "INSERT INTO img_wikidata_id (img_id, wikidata_id) "
      "VALUES (%s, %s)")
    insert_new_img_path = (
      "INSERT INTO img_path (img_id, path) "
      "VALUES (%s, %s)")
    
    try:
      print(file_path)
      cur.execute(insert_new_img_url, (wikidata_id, url))
      img_urls_in_db.add((wikidata_id, url))
      img_id = cur.lastrowid
      cur.execute(insert_new_img_wikidata_id, (img_id, wikidata_id))
      cur.execute(insert_new_img_path, (img_id, file_path))
      connection.commit()
    except Exception:
      traceback.print_exc()

def DownloadImages(entity_name, entity_url):
  wikidata_id = ExtractEntityID(entity_url)
  if not wikidata_id: return 
  insert_new_name = (
    "INSERT INTO names (wikidata_id, name) "
    "VALUES (%s, %s)")
  if wikidata_id not in wikidata_ids_in_db: 
    cur.execute(insert_new_name, (wikidata_id, entity_name))
    wikidata_ids_in_db.add(wikidata_id)

  img_dir_path = MakeEntityImgDir(wikidata_id)
  for i, img_url in enumerate(ExtractImageURLs(entity_url)):
    if (wikidata_id, img_url) in img_urls_in_db: 
      print(f"still exists: ({wikidata_id}, {img_url})")
      continue
    filename = 'image_' + str(i).zfill(4) + '.jpg'
    img_file_path = os.path.join(img_dir_path, filename)
    DownloadImage(url=img_url, file_path=img_file_path, wikidata_id = wikidata_id)

entity_names_urls = ExtractEntityURLs(category='People_by_name')
# entity_names_urls = ExtractEntityURLs(category='Dog_breeds_by_name')
for entity_name, entity_url in entity_names_urls:
  DownloadImages(entity_name, entity_url)
connection.close() 