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

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) 

data_dir = "../../../data/clean"

# TODO: 暫定的に解消したが、出力の形式をもっと固定する必要がある
# TODO: まだごく一部のエンティティはmasking後のtextが空になってしまうが、数としては少ないのでスルー。
def create_messages_for_masking_to_super_category(category, entity_name, text):

    messages_for_masking_to_super_category=[
        {"role": "system", "content": "You are a helpful annotator of sentences."},
        {"role": "user", "content": f"Please convert 'Entity name' of following sentences to 'this {category}'."},
        # {"role": "user", "content": f"Please convert entity name of following sentences to 'the {category}'."},
        {"role": "assistant", "content": f"Entity name: {entity_name}"},
        {"role": "assistant", "content": f"Convert from following sentences:\n{text}"},
    ]

    return messages_for_masking_to_super_category


# TODO: 
# 生成されるmasked questionが1つずれているので解決する
# this categoryが"us_politician"から"US Politician"になるように変更する
def mask_entity_name_by_category(category, start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    category_dir = get_category_dir(category)
    entity_to_qas_path = get_save_path(category_dir, start_idx, end_idx)

    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f)

    for i, entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"Masking questions for {entity_id}, idx: {start_idx+i}")

        try:
        # TODO: QAごとではなくエンティティごとに複数のQAを一気に処理するのは、gptへのリクエスト数を減らせるため
            entity_to_qas[entity_id] = rephrase_questions_by_entity(entity_to_qas[entity_id])
        except Exception as e:
            logger.error(e)

        try:

            # すでにmasking済みの場合はスキップ
            cnt = 0
            for qa in qas[entity_id]:
                if "Q_rephrase_mask" in qa and qa["Q_rephrase_mask"] != "":
                    cnt += 1
            if cnt == len(qas[entity_id]):
                logger.info(f"Skip because already masked questions for {entity_id}")
                continue
            
            questions_merge = merge_text(qas[entity_id], "Q_rephrase")
            messages_for_masking_to_super_category = create_messages_for_masking_to_super_category(category, entity_name, questions_merge)
            questions_masked = gpt_request(messages_for_masking_to_super_category)

            # questions_masked = mask_entity_name(category, id_to_name[entity_id], questions_merge)
            questions_masked_list = questions_masked.split("\n")
            for i, qa in enumerate(qas[entity_id]):
                qa["Q_rephrase_mask"] = questions_masked_list[i]
                if qa["Q_rephrase_mask"] == "":
                    print('qa["Q_rephrase_mask"] == ""')
                    print(questions_masked)
        except Exception as e:
            logger.error(f"entity_id: {entity_id}")
            logger.error(e)
    with open(f"{category_dir}/qas_{start_idx}.json", 'w') as f:
        json.dump(qas, f, indent=2)

def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        mask_entity_name_by_category(category)

if __name__ == "__main__":
    main()

