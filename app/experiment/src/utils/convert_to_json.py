import json, os

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

data_dir = "../../../data/clean"

def convert_text_to_dict(output):
        qas = output.split('\n\n')
        qas_dict_list = []
        # TODO: propose more strict way to extract question and answer
        for qa in qas:
            try:
                question, answer = qa.split('\n')
                qas_dict_list.append({"Q": question[3:], "A": answer[3:]})
            except Exception as e:
                logger.error(f"qa: {qa}")
                logger.error(e)
        return qas_dict_list

def convert_text_to_dict_by_categories(categories):
    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        entity_text_files = os.listdir(f"{category_dir}/gpt_3_output")
        qas = {}
        for entity_text_file in entity_text_files:
            try:
                entity_id = entity_text_file.split(".")[0]
                with open(f"{category_dir}/gpt_3_output/{entity_text_file}", 'r') as f:
                    output = f.read()
                qas[entity_id] = convert_text_to_dict(output)
            except Exception as e:
                logger.error(f"entity_text_file: {entity_text_file}")
                logger.error(f"entity_id: {entity_id}")
                logger.error(f"output: {output}")
                logger.error(e)
        with open(f"{category_dir}/qas.json", 'w') as f:
            json.dump(qas, f, indent=2)

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    convert_text_to_dict_by_categories(categories)

if __name__ == "__main__":
    main()