import json

import logging, logging.config
from yaml import safe_load
with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

def clean_relations_text(wikidata):
    # delete values with starting with "http"
    print(f"len(wikidata): {len(wikidata)}")
    for val in wikidata.values():
        val["text_clean"] = val["text"]
        for key, relation_list in val["relations"].items():
            relation_str = ", ".join(relation_list)
            val["text"] += f"'{key}': {relation_str}. "
    return wikidata

def clean_relations_text_by_category(category):
    # for category in categories:
    print(category)
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_filtered.json') as f:
        wikidata = json.load(f)
    wikidata = clean_relations_text(wikidata)
    with open(f"{category_dir}/wikidata_filtered.json", "w") as f:
        json.dump(wikidata, f, indent=2)
    
def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        clean_relations_text_by_category(category)

if __name__ == "__main__":
    main()