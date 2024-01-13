import re
import sys
import json 
import traceback
import os

sys.path.append("./utils")
from util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


# wikimediaとwikipediaの両方に存在するエンティティのみを抽出する
def filter_existing_wikipedia(category):
    print("filter_existing_wikipedia")
    category_dir = f"../../../data/clean/{category}"
    # wikipediaディレクトリから、記事名一覧を取得し、それらのファイル名からidを抽出する
    wikipedia_dir = f"{category_dir}/wikipedia"
    entity_text_files = os.listdir(wikipedia_dir)
    ids_with_article = []
    for entity_text_file in entity_text_files:
        id = entity_text_file.split(".")[0]
        ids_with_article.append(id)
    print(f"len(ids_with_article): {len(ids_with_article)}")

    # wikidata_with_commons.jsonから、wikipediaに記事が存在するエンティティのみを抽出する
    with open(f'{category_dir}/wikidata_with_commons.json') as f:
        wikidata = json.load(f)
    print(f"len(wikidata) before filtering: {len(wikidata)}")

    del_ids = []
    for id in wikidata:
        if not id in ids_with_article:
            del_ids.append(id)

    print(f"len(del_ids): {len(del_ids)}")
    
    # print(del_ids[:20])

    for id in del_ids:
        del wikidata[id]

    print(f"len(wikidata) after filtering: {len(wikidata)}")
    with open(f'{category_dir}/wikidata_filtered.json', 'w') as f:
        json.dump(wikidata, f, indent=4)


# wikimediaとwikipediaの両方に存在するエンティティのみを抽出する
def filter_existing_wikimedia(category):
    print("filter_existing_wikimedia")
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata.json') as f:
        wikidata = json.load(f)
    print(f"len(wikidata) before filtering: {len(wikidata)}")

    del_ids = []
    for id in wikidata:
        # commonsに存在しない
        if not ("Commons category" in wikidata[id]["relations"] or "image" in wikidata[id]["relations"]):
            del_ids.append(id)
    # print(del_ids[:20])

    for id in del_ids:
        del wikidata[id]

    print(f"len(wikidata) after filtering: {len(wikidata)}")
    with open(f'{category_dir}/wikidata_with_commons.json', 'w') as f:
        json.dump(wikidata, f, indent=4)


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(category)

        # "image" と"Commons category"のどちらかが存在するエンティティのみを抽出する
        # filter_existing_wikipediaは、記事を抽出した後に実行する
        filter_existing_wikimedia(category=category)
        # filter_existing_wikipedia(category=category)


if __name__ == "__main__":
    main()