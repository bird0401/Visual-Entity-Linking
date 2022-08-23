import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
from fake_useragent import UserAgent
import pathlib
import time
from requests.exceptions import Timeout

def download_images(url, file_path):
  ua = UserAgent()
  header = {'user-agent':ua.chrome}
  try:
    r = requests.get(url, stream=True, headers=header, timeout=10)
  except Timeout:
    print('Timeout has been raised.')
  time.sleep(1)

  if r.status_code == 200:
    with open(file_path, "wb") as f:
      f.write(r.content)
  else: print(f'error {r.status_code}')

# collect instance urls
first_loop=True
move_to_next_page=True
instance_urls=[]

while move_to_next_page:
  # requests to wikimedia regarding category which I want to exploit images
  wikimedia_url = 'https://commons.wikimedia.org'
  category='Dog_breeds_by_name'
  category_url=f'/wiki/Category:{category}'
  
  if first_loop: 
    try:
      res = requests.get(wikimedia_url+category_url, timeout=10)
    except Timeout:
      print('Timeout has been raised.')
    time.sleep(1)
    first_loop=False
  else: 
    try:
      res = requests.get(wikimedia_url+next_page_url, timeout=10)
    except Timeout:
      print('Timeout has been raised.')
    time.sleep(1)

  soup = BeautifulSoup(res.text, "html.parser")
  try:  next_page_url=soup.find_all(text="next page")[0].parent.attrs['href']
  except: move_to_next_page=False

  elems=soup.find_all(class_="CategoryTreeItem")

  for elem in elems:
    instance_url=elem.find('a').attrs['href']
    instance_urls.append(instance_url)

# len(instance_urls)

# collect image urls of each instance
for instance_url in instance_urls:
  try:
      res = requests.get(wikimedia_url+instance_url, timeout=10)
  except Timeout:
      print('Timeout has been raised.')
  time.sleep(1)
  soup = BeautifulSoup(res.text, "html.parser")

  extiw_class=soup.select('a[href^="https://www.wikidata.org/wiki/Q"]')
  try:  wikidata_id=pathlib.Path(extiw_class[0].attrs['href']).stem
  except:  continue
  path = "./imgs/" + wikidata_id
  os.makedirs(path,exist_ok=True)

  img_urls=[]
  move_to_next_page=True

  while move_to_next_page:
    try:
      res = requests.get(wikimedia_url+instance_url, timeout=10)
    except Timeout:
      print('Timeout has been raised.')
    time.sleep(1)
    soup = BeautifulSoup(res.text, "html.parser")

    try:  instance_url=soup.find_all(text="next page")[0].parent.attrs['href']
    except: move_to_next_page=False
    
    image_classes=soup.find_all(class_="image")
    for image_class in image_classes:
      img_url=image_class.img.attrs['src']
      img_urls.append(img_url)
      

  for index, url in enumerate(img_urls):
      filename = 'image_' + str(index) + '.jpg'
      image_path = os.path.join(path, filename)
      print(url)
      print(image_path)
      download_images(url=url, file_path=image_path)
  print()
