import openai
import os, json, pickle
from util import *

from dotenv import load_dotenv
load_dotenv()
openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# TODO: 
# 生成されるmasked questionが1つずれているので解決する
# this categoryが"us_politician"から"US Politician"になるように変更する


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def mask_entity_name(category, entity_name, text):
    try:
        # TODO: 暫定的に解消したが、出力の形式をもっと固定する必要がある
        # TODO: まだごく一部のエンティティはmasking後のtextが空になってしまうが、数としては少ないのでスルー。
        messages=[
            {"role": "system", "content": "You are a helpful annotator of sentences."},
            {"role": "user", "content": f"Please convert 'Entity name' of following sentences to 'this {category}'."},
            # {"role": "user", "content": f"Please convert entity name of following sentences to 'the {category}'."},
            {"role": "assistant", "content": f"Entity name: {entity_name}"},
            {"role": "assistant", "content": f"Convert from following sentences:\n{text}"},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
        return response.choices[0]["message"]["content"]
    except Exception as e:
        logger.error(f"entity_name: {entity_name}")
        logger.error(f"text:\n{text}")
        logger.error(e)

def mask_entity_name_by_categories(categories, start_idx=0, end_idx=5000):
    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        logger.info(f"open: {category_dir}/qas_{start_idx}.json")
        with open(f"{category_dir}/qas_{start_idx}.json") as f:
            qas = json.load(f)
        with open(f"{category_dir}/id_to_name.json") as f:    
            id_to_name = json.load(f)
        # with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
        #     id_to_name = pickle.load(f)
        ids = list(qas.keys())
        # ids = ["Q25172100"] # テスト用
        # for i, entity_id in enumerate(ids[start_idx:end_idx]):
        for i, entity_id in enumerate(ids):
            logger.info(f"Masking questions for {entity_id} ({i+1}/{len(qas)})")
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
                questions_masked = mask_entity_name(category, id_to_name[entity_id], questions_merge)
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
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    mask_entity_name_by_categories(categories)

if __name__ == "__main__":
    main()

