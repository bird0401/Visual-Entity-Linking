from bs4 import BeautifulSoup
import re, os, traceback
from app.scraping.src.utils.util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def extract_next_page_url(url, text="next page"):
    try:
        res = fetch(url)
        soup = BeautifulSoup(res.text, "html.parser")
        t = soup.find(text=text)
        return to_abs_url(related_url=t.parent.attrs["href"])
    except Exception:
        traceback.print_exc()
        return None

def extract_entity_urls(category):
    entity_list_page_url = to_abs_url(related_url=f"/wiki/Category:{category}")

    while entity_list_page_url:
        res = fetch(entity_list_page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        try:
            elems = soup.find_all(class_="CategoryTreeItem")
            for elem in elems:
                entity_name = elem.find("a").text
                entity_url = to_abs_url(related_url=elem.find("a").attrs["href"])
                if entity_name and entity_url:
                    yield entity_name, entity_url
                else:
                    continue
        except Exception:
            traceback.print_exc()
        entity_list_page_url = extract_next_page_url(entity_list_page_url)

def make_entity_dir(id):
    save_dir = f"../wikipedia/{id}"
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    return save_dir

def extract_wikipedia_url(entity_url):
    res = fetch(entity_url)
    soup = BeautifulSoup(res.text, "html.parser")
    wikipedia_url = soup.find(href=re.compile("^https://en.wikipedia.org/wiki/"), text="Wikipedia").attrs["href"]
    logger.info(f"wikipedia_url: {wikipedia_url}")
    return wikipedia_url

def download_text(soup, save_dir):
    p_tags = soup.find_all('p')
    text = "\n".join([tag.get_text().strip() for tag in p_tags])
    file_path = f"{save_dir}/entity_page.txt"
    # logger.info(f"text file_path: {file_path}")
    with open(file_path, "w") as f:
        f.write(text)
        
def download_image(soup, save_dir):
    try:
        infobox_image = soup.find(class_="infobox-image")
        img_url = f"https:{infobox_image.img.attrs['src']}"
        logger.info(f"img_url: {img_url}")
        res = fetch(img_url)
        file_path = f"{save_dir}/image.jpg"
        # logger.info(f"image file_path: {file_path}")
        with open(file_path, "wb") as f:
            f.write(res.content)
    except Exception:
        traceback.print_exc()

def download_image_and_text(entity_url):
    # logger.info(f"entity_name: {entity_name}")
    logger.info(f"entity_url: {entity_url}")
    try:
        wikipedia_url = extract_wikipedia_url(entity_url)
        res = fetch(wikipedia_url)
        soup = BeautifulSoup(res.text, "html.parser")   
        dir_name = entity_url[44:][:255]
        save_dir = make_entity_dir(dir_name)
        download_text(soup, save_dir)
        download_image(soup, save_dir)
        print()
    except Exception:
        traceback.print_exc()

# Change
# - category
category = "Politicians_of_the_United_States_by_name"
entity_names_urls = extract_entity_urls(category=category)
for _, entity_url in entity_names_urls:
    download_image_and_text(entity_url)
# for i, (_, entity_url) in enumerate(entity_names_urls):
#     download_image_and_text(entity_url)
#     if i > 10:
#         break