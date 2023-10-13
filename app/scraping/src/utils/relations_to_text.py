import json

import logging, logging.config
from yaml import safe_load
with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

def relations_to_text(wikidata):
    for val in wikidata.values():
        val["text"] = ""
        for key, relation_list in val["relations"].items():
            relation_str = ", ".join(relation_list)
            val["text"] += f"'{key}': {relation_str}. "
    return wikidata

def relations_to_text_by_categories(categories):
    for category in categories:
        print(category)
        category_dir = f"../../../data/clean/{category}"
        with open(f'{category_dir}/wikidata.json') as f:
            wikidata = json.load(f)
        wikidata = relations_to_text(wikidata)
        with open(f"{category_dir}/wikidata.json", "w") as f:
            json.dump(wikidata, f, indent=2)
    
def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    relations_to_text_by_categories(categories)

if __name__ == "__main__":
    main()