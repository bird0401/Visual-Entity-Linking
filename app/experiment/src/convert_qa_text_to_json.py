import json, traceback
import logging
import logging.config
from yaml import safe_load

from config import *

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def convert_text_to_dict(gpt_output):
    gpt_output = gpt_output.rstrip()
    qas = gpt_output.split('\n\n')
    if len(qas) == 0:
        return None
    qas_dict_list = []
    # TODO: propose more strict way to extract question and answer
    for qa in qas:
        if qa[0] != 'Q':
            continue
        try:
            question, answer = qa.split('\n')
            if question[0] != 'Q' or answer[0] != 'A':
                continue
            qas_dict_list.append({"Q": question[3:], "A": answer[3:]})
        except Exception as e:
            logger.error(f"gpt_output: {gpt_output}")
            logger.error(f"len(qas): {len(qas)}")
            logger.error(f"qa: {qa}")
            traceback.print_exc()
    return qas_dict_list


def convert_text_to_dict_by_category(category, start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    category_dir = get_category_dir(category)
    save_path = get_save_path(category_dir, start_idx, end_idx)
    
    with open(f"{category_dir}/ids.json") as f:
        entity_ids = json.load(f)
    logger.info(f"len(entity_ids): {len(entity_ids)}")

    qas = {}
    gpt_output_dir = get_gpt_output_dir(category_dir)
    logger.info(f"len(entity_ids), start_idx, end_idx: {len(entity_ids)}, {start_idx}, {end_idx}")

    for entity_id in entity_ids[start_idx:end_idx]:
        with open(f"{gpt_output_dir}/{entity_id}.txt", 'r') as f:
            gpt_output = f.read()

        if not gpt_output:
            logger.info(f"Skip {entity_id} because output is empty")
            continue

        gpt_output_dict_list = convert_text_to_dict(gpt_output)
        if not gpt_output_dict_list:
            logger.info(f"Skip {entity_id} because output_dict_list is empty")
            continue

        qas[entity_id] = gpt_output_dict_list

    with open(save_path, 'w') as f:
        json.dump(qas, f, indent=2)


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        convert_text_to_dict_by_category(category, 0, 3)


if __name__ == "__main__":
    main()