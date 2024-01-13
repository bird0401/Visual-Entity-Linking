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
        output = output.rstrip()
        qas = output.split('\n\n')
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
                logger.error(e)
                logger.error(f"output: {output}")
                logger.error(f"len(qas): {len(qas)}")
                logger.error(f"qa: {qa}")
        return qas_dict_list

def convert_text_to_dict_by_categories(categories, start_idx=0, end_idx=5000):
    for category in categories:
        logger.info(f"category: {category}")
        # if limit:
        #     logger.info(f"limit: {limit}")
        category_dir = f"{data_dir}/{category}"
        save_file_path = f"{category_dir}/qas_{start_idx}.json"
        # QAのみのファイルで上書き保存されないためスキップ
        if os.path.exists(save_file_path):
            logger.info(f"{save_file_path} already exists. skip this category.")
            continue
        # if limit:
        #     entity_text_files = os.listdir(f"{category_dir}/gpt_3_output")[:limit]
        # else:
        entity_text_files = os.listdir(f"{category_dir}/gpt_3_output")

        qas = {}
        logger.info(f"len(entity_text_files), start_idx, end_idx: {len(entity_text_files)}, {start_idx}, {end_idx}")
        # for entity_text_file in entity_text_files:
        # ここでエンティティを分割して並行処理を行うことで高速化する
        for entity_text_file in entity_text_files[start_idx:end_idx]:
            entity_id = entity_text_file.split(".")[0]
            with open(f"{category_dir}/gpt_3_output/{entity_text_file}", 'r') as f:
                output = f.read()
            if output:
                output_dict_list = convert_text_to_dict(output)
            if output_dict_list:
                qas[entity_id] = output_dict_list
        with open(save_file_path, 'w') as f:
            json.dump(qas, f, indent=2)

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    convert_text_to_dict_by_categories(categories)

if __name__ == "__main__":
    main()