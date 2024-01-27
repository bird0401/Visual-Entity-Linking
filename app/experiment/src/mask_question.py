import json
from tqdm import tqdm

from util import *
from config import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def capitalize_category_name(category):
    if category == "us_politician":
        return "US Politician"
    else:
        return category.capitalize()
    

def create_messages_for_masking_to_super_category(category, entity_name, text):

    messages_for_masking_to_super_category=[
        {"role": "system", "content": "You are a helpful annotator of sentences."},
        {"role": "assistant", "content": f"Entity name: {entity_name}"},
        {"role": "user", "content": f"Convert Entity name of following sentences to 'this {category}'."},
        {"role": "assistant", "content": f"{text}"},
    ]

    return messages_for_masking_to_super_category


def mask_questions_by_entity(qas, category, id_to_name,  entity_id):
    # Skip if all questions are already masked
    # cnt = 0
    # for i, qa in enumerate(qas):
    #     if "Q_rephrase_mask" in qa and qa["Q_rephrase_mask"]:
    #         cnt += 1
    # if cnt == len(qas):
    #     logger.info(f"Skip because all questions are already masked")
    #     return    

    capitalized_category = capitalize_category_name(category)
    entity_name = id_to_name[entity_id]

    # QAごとではなくエンティティごとに複数のQAを一気に処理するのは、gptへのリクエスト数を減らせるため
    questions_merge = merge_list_text(qas, "Q_rephrase")
    messages_for_masking_to_super_category = create_messages_for_masking_to_super_category(capitalized_category, entity_name, questions_merge)
    
    # for debugging gpt output format
    # print("messages_for_masking_to_super_category")
    # for message in messages_for_masking_to_super_category:
    #     print(message)
    # print()
    
    questions_masked = gpt_request(messages_for_masking_to_super_category)
    # print("questions_masked")
    # print(questions_masked)
    # print()
    questions_masked_list = questions_masked.split("\n")

    for i, qa in enumerate(qas):
        qa["Q_rephrase_mask"] = questions_masked_list[i]
        # if qa["Q_rephrase_mask"] == "":
        #     print('qa["Q_rephrase_mask"] == ""')
        #     print(questions_masked)
    return qas


def mask_questions_by_category(category, start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    category_dir = get_category_dir(category)
    entity_to_qas_path = get_entity_to_qas_path(category, start_idx, end_idx)

    # カテゴリごとにそのカテゴリのidと名前の対応付け用ファイルが存在
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)

    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f)

    for i, entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"Masking questions for {entity_id}, idx: {start_idx+i}")

        try:
            entity_to_qas[entity_id] = mask_questions_by_entity(entity_to_qas[entity_id], category, id_to_name, entity_id)
        except Exception as e:
            logger.error(e)

    with open(entity_to_qas_path, 'w') as f:
        json.dump(entity_to_qas, f, indent=2)


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        mask_questions_by_category(category, 0, 3)


if __name__ == "__main__":
    main()
