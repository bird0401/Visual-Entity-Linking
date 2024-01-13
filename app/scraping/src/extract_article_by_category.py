import re
import os
import traceback
import json

import sys
sys.path.append("./utils")
from util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def extract_wikipedia_url(entity_id):
    try:
        wikidata_url = f"https://www.wikidata.org/wiki/{entity_id}"
        logger.info(f"wikidata_url: {wikidata_url}")
        soup = parse_to_soup(wikidata_url)
        wikipedia_url = soup.find(href=re.compile("^https://en.wikipedia.org/wiki/")).attrs["href"]
        logger.info(f"wikipedia_url: {wikipedia_url}")
        return wikipedia_url
    except AttributeError:
        logger.info(f"no article: {wikidata_url}")
    except Exception:
        traceback.print_exc()


def fetch_article(wikipedia_url):
    try:
        soup = parse_to_soup(wikipedia_url)
        p_tags = soup.find_all('p')
        article = "\n".join([tag.get_text().strip() for tag in p_tags])
        return article
    except Exception:
        traceback.print_exc()


def download_article(entity_id, category_dir):
    # logger.info(f"entity_id: {entity_id}")
    wikipedia_url = extract_wikipedia_url(entity_id)
    if not wikipedia_url:
        return None
    article = fetch_article(wikipedia_url)
    if article:
        with open(f"{category_dir}/wikipedia/{entity_id}.txt", "w") as f:
            f.write(article) 

# start_indexとend_indexは、並行処理において、どのidからどのidまでを処理するかを決めるためのもの
def extract_article_by_category(category, start_index=0, end_index=1000000):
    data_dir = f"../../../data/clean"
    category_dir = f"{data_dir}/{category}"
    with open(f'{category_dir}/wikidata_with_commons.json') as f:
        ids_file = json.load(f)
    ids = list(ids_file.keys())
    logger.info(f"len(ids): {len(ids)}")
    if not os.path.isdir(f"{category_dir}/wikipedia"):
        os.makedirs(f"{category_dir}/wikipedia")
    # for id in ids[:10]: # テスト用
    for i, id in enumerate(ids[start_index:end_index]):
        if i % 1000 == 0:
            logger.info(f"PROGRESS: {i}/{len(ids[start_index:end_index])}")
        download_article(id, category_dir)
        print()


# wikidataのURLからスクレイピングすることでwikipediaのURLを取得する
# wikidata上のrelationにwikipedia記事関する項目存在しないため
def main():
    categories = ["aircraft" ]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        extract_article_by_category(category)


if __name__ == "__main__":
    main()