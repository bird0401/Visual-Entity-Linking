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

def extract_entity_name(entity_id):
    try:
        wikidata_url = f"https://www.wikidata.org/wiki/{entity_id}"
        soup = parse_to_soup(wikidata_url)        
        entity_name = soup.find(class_="wikibase-title-label").get_text()
        logger.info(f"entity_name: {entity_name}")
        return entity_name
    except Exception:
        traceback.print_exc()

def main():
    data_dir = f"../../../data/clean"
    # categories = ["aircraft"]
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        ids_file = f"{data_dir}/{category}/csv/ids.csv"
        entity_ids = pd.read_csv(ids_file)["wikidata_id"]
        entity_ids_names = {}
        for entity_id in entity_ids:
            entity_name = extract_entity_name(entity_id)
            if entity_name:
                entity_ids_names[entity_id] = entity_name
        ids_and_names = pd.DataFrame(entity_ids_names.items(), columns=["wikidata_id", "entity_name"])
        print(ids_and_names)
        ids_and_names.to_csv(f"{data_dir}/{category}/csv/entity_ids_names.csv", index=False)

if __name__ == "__main__":
    main()