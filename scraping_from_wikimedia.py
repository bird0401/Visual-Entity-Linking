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
database, host = 'scraping', 'localhost'

connection = mysql.connector.connect(
    user = mysql_user,
    password = mysql_password,
    host = host,
    database = database,
    )

cur = connection.cursor()
cur.execute("SELECT img_url FROM img_urls")
img_urls_in_db = cur.fetchall()
cur.execute("SELECT wikidata_id FROM names")
wikidata_ids_in_db = cur.fetchall()

insert_new_name = (
  "INSERT INTO names (wikidata_id, name) "
  "VALUES (%s, %s)")
insert_new_img_url = (
  "INSERT INTO img_urls (img_url) "
  "VALUE (%s)")
insert_new_img_wikidata_id = (
  "INSERT INTO img_wikidata_id (img_id, wikidata_id) "
  "VALUES (%s, %s)")
insert_new_img_path = (
  "INSERT INTO img_path (img_id, path) "
  "VALUES (%s, %s)")


ua = UserAgent()
header = {'user-agent':ua.chrome}
wikimedia_url = 'https://commons.wikimedia.org'

def ToAbsURL(related_url = '/wiki/Category'):
  base_url = wikimedia_url
  return base_url+related_url
  
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def Fetch(url):
  """
  add below handlings to normal request
  - 3 times retry
  - 1s sleep
  - exception handling
  """

  # when 200<=res.status_code<300 execute code in try statement
  # this time, 200 will return because of success of get request is 200
  try: 
    res = requests.get(url, headers=header, timeout=10)
  except Timeout:
    print('Timeout has been raised.')
    return None
  except:
    traceback.print_exc()
    return None
  
  time.sleep(1) 
  return res

def ExtractNextPageURL(url, text="next page"):
  res = Fetch(url)
  soup = BeautifulSoup(res.text, "html.parser")
  try:
    t=soup.find(text=text)
    if t: return ToAbsURL(related_url = t.parent.attrs['href'])
  except: 
    traceback.print_exc()
    return None

def ExtractEntityURLs(category):
  entity_urls=[]
  entity_list_page_url=ToAbsURL(related_url = f'/wiki/Category:{category}')

  while entity_list_page_url:
    res = Fetch(entity_list_page_url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    try:
      elems=soup.find_all(class_="CategoryTreeItem")
      for elem in elems:
        entity_url=elem.find('a').attrs['href']
        yield ToAbsURL(related_url = entity_url)
    except:
      traceback.print_exc()

    print(entity_list_page_url)
    entity_list_page_url=ExtractNextPageURL(entity_list_page_url)

def ExtractEntityID(entity_url):
  try: 
    res = Fetch(entity_url)
    soup = BeautifulSoup(res.text, "html.parser") 
    wikidata_url=soup.find(href=re.compile("^https://www.wikidata.org/wiki/Q")).attrs["href"]
    wikidata_id=pathlib.Path(wikidata_url).stem
    return wikidata_id
  except:
    traceback.print_exc()
    return None

def MakeEntityImgDir(id):
  img_path = "./imgs/" + id
  os.makedirs(img_path,exist_ok=True)
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
      except: 
        traceback.print_exc()
        return None

def ExtractImageURLs(entity_img_list_page_url):
  """
  Image Page is the page which contains image, description, bottons, etc.
  after extract Image Page URL, I should extract image url from this Page 
  """
  while entity_img_list_page_url:
    res = Fetch(entity_img_list_page_url)
    soup = BeautifulSoup(res.text, "html.parser")
    try:
      image_classes=soup.find_all(class_="galleryfilename galleryfilename-truncate")
      for image_class in image_classes:
        img_page_url=ToAbsURL(image_class.attrs['href'])
        img_url = ExtractImageURL(img_page_url)
        if img_url: yield img_url
    except:
      traceback.print_exc()
    entity_img_list_page_url=ExtractNextPageURL(entity_img_list_page_url)

def DownloadImage(url, file_path, wikidata_id):
  res=Fetch(url)
  if res: 
    with open(file_path, "wb") as f: f.write(res.content)
    cur.execute(insert_new_img_url, (url))
    img_id = cur.execute("SELECT LAST_INSERT_ID();")
    cur.execute(insert_new_img_wikidata_id, (img_id, wikidata_id))
    cur.execute(insert_new_img_path, (img_id, file_path))
    connection.commit()

def DownloadImages(entity_name, entity_url):
  wikidata_id = ExtractEntityID(entity_url)
  if not wikidata_id: return None
  if wikidata_id not in wikidata_ids_in_db: cur.execute(insert_new_name, (wikidata_id, entity_name))
  img_dir_path = MakeEntityImgDir(wikidata_id)
  for i, img_url in enumerate(ExtractImageURLs(entity_url)):
    if img_url in img_urls_in_db: continue
    filename = 'image_' + str(i).zfill(3) + '.jpg'
    img_file_path = os.path.join(img_dir_path, filename)
    print(f"URL: {img_url}")
    print(f"Path: {img_file_path}")
    DownloadImage(url=img_url, file_path=img_file_path, wikidata_id = wikidata_id)

 # we can iterate only one time because entity_urls is iterator
entity_names_urls=ExtractEntityURLs(category='Dog_breeds_by_name')
for entity_name, entity_url in entity_names_urls:
  DownloadImages(entity_name, entity_url)
connection.close() 