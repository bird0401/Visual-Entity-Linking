import re, traceback
from util import *
import pandas as pd

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

        
def extract_entity_ids(ids_file):
    try:
        ids = pd.read_csv(ids_file)["wikidata_id"]
        logger.info(f"len(ids): {len(ids)}")
        return ids
    except Exception:
        traceback.print_exc()

def extract_wikipedia_url(entity_id):
    try:
        wikidata_url = f"https://www.wikidata.org/wiki/{entity_id}"
        soup = parse_to_soup(wikidata_url)
        wikipedia_url = soup.find(href=re.compile("^https://en.wikipedia.org/wiki/")).attrs["href"]
        logger.info(f"wikipedia_url: {wikipedia_url}")
        return wikipedia_url
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

def download_article(entity_id):
    logger.info(f"entity_id: {entity_id}")
    wikipedia_url = extract_wikipedia_url(entity_id)
    article = fetch_article(wikipedia_url)
    download_text(article, f"{article_dir}/{entity_id}.txt")


data_dir = f"../../../data/clean"
article_dir = f"{data_dir}/wikipedia"
make_dir(article_dir)
categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
for category in categories:
    ids_file = f"{data_dir}/{category}/csv/ids.csv"
    entity_ids = extract_entity_ids(ids_file)
    for entity_id in entity_ids:
        download_article(entity_id)
        print()