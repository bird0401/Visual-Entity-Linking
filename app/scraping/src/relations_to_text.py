import json

import logging, logging.config
from yaml import safe_load
with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

def create_texts(relations):
    id_to_text = {}
    for id in relations:
        text_set = set()
        for relation in relations[id]:
            for key in relation:
                text_set.add(f"{key} is {relation[key]['value']}")
        id_to_text[id] = ". ".join(text_set)
        id_to_text[id] += "."
    return id_to_text
    
def main():
    categories = ["athlete"]
    for category in categories:
        category_dir = f"../../../data/clean/{category}"
        with open(f'{category_dir}/relations.json') as f:
            relations = json.load(f)
        id_to_text = create_texts(relations)
        with open(f"{category_dir}/id_to_text_by_relation.json", "w") as f:
            json.dump(id_to_text, f, indent=2)

if __name__ == "__main__":
    main()