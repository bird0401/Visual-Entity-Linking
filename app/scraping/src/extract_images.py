import os
import sys
import json 
import traceback

sys.path.append("./utils")
from util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def download_image_from_wikipedia(image_url, save_dir):
    try:
        print("From Wikipedia")
        print(f"image_url: {image_url}")
        res = fetch(image_url)
        file_path = f"{save_dir}/image_wikipedia.jpg"
        with open(file_path, "wb") as f:
            f.write(res.content)
    except Exception:
        traceback.print_exc()


def download_image(url, file_path):
    res = fetch(url)
    if res:
        logger.info(file_path)
        with open(file_path, "wb") as f:
            f.write(res.content)


def download_image_from_wikimedia(entity_url, save_dir):
    try:
        print("From Commons")
        print(f"entity_url: {entity_url}")

        for i, img_url in enumerate(extract_image_urls(entity_url)):
            filename = "image_" + str(i).zfill(4) + ".jpg"
            save_file_path = f"{save_dir}/{filename}"
            download_image(url=img_url, file_path=save_file_path)

    except Exception:
        traceback.print_exc()


def extract_image_url(img_page_url):
    try:
        res = fetch(img_page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        l = soup.find(class_="fullImageLink")
        if l:
            img_url = l.a.attrs["href"]
            return img_url
        else:
            print("can't extract image URL")  # for example, in the case that the file is mp3
    except Exception:
        traceback.print_exc()
        return None


def extract_next_page_url(url, text="next page"):
    res = fetch(url)
    soup = BeautifulSoup(res.text, "html.parser")
    try:
        t = soup.find(text=text)
        if t:
            return to_abs_url(related_url=t.parent.attrs["href"])
    except Exception:
        traceback.print_exc()
        return None
    

def extract_image_urls(entity_img_list_page_url):
    """
    Image Page is the page which contains an image, description, bottons, etc.
    after extract Image Page URL, extract image url from this Page
    """
    # first_page = True
    while entity_img_list_page_url:
        res = fetch(entity_img_list_page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        try:
            image_classes = soup.find_all(class_="galleryfilename galleryfilename-truncate")
            # if first_page and len(image_classes) < 5:
            #     logger.info(f"{entity_img_list_page_url} has only {len(image_classes)} images")
            #     return
            for image_class in image_classes:
                img_page_url = to_abs_url(related_url=image_class.attrs["href"])
                img_url = extract_image_url(img_page_url)
                if img_url:
                    yield img_url
                else:
                    continue
        except Exception:
            traceback.print_exc()
        entity_img_list_page_url = extract_next_page_url(entity_img_list_page_url)
        # first_page = False


def extract_images(category, start_index=0, end_index=5000):
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_filtered.json') as f:
        wikidata = json.load(f)
    ids = list(wikidata.keys())
    logger.info(f"len(ids), start_index, end_index: {len(ids)}, {start_index}, {end_index}")
    for i, id in enumerate(ids[start_index:end_index]):
        if i % 1000 == 0:
            logger.info(f"PROGRESS: {i}/{len(ids[start_index:end_index])}")
        save_dir = f"{category_dir}/images/{id}"
        
        if os.path.isdir(save_dir) and len(os.listdir(save_dir)) > 0:
            logger.info(f"{id} is already downloaded")
            continue

        os.makedirs(save_dir, exist_ok=True)
        if "image" in wikidata[id]["relations"]:
            download_image_from_wikipedia(wikidata[id]["relations"]["image"][0], save_dir)
        if "Commons category" in wikidata[id]["relations"]:
            Commons_category = wikidata[id]["relations"]["Commons category"][0].replace(" ", "_") # wikidataのrelationのvalueリストなので注意
            commons_category_url = to_abs_url(related_url=f"/wiki/Category:{Commons_category}")
            download_image_from_wikimedia(commons_category_url, save_dir)


# TODO: filerとextractを分割する
# また、ここでは上位カテゴリ名を指定しているが、wikidataでは下位カテゴリから直接アクセスする
# 画像収集元がwikimediaのみだと、wikidata上のエンティティのうちかなりの数が対象外となってしまうため、wikipedia上の画像が存在するエンティティも収集対象とする。
def main():
    categories = ["aircraft" ]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(category)
        # カテゴリのwikidata relationsを取得し、それぞれのエンティティのwikimediaカテゴリを取得する
        extract_images(category=category, start_index=0, end_index=1000000)


if __name__ == "__main__":
    main()