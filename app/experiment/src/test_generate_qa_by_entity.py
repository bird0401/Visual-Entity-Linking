# import sys
# sys.path.append("utils")

from config import *
from util import *
from generate_qa import *
from convert_qa_text_to_json import *
from rephrase_question import *
from mask_question import *
from app.experiment.src.answer_and_evaluate import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# 8時間で5000エンティティが目安

# Progress: 
# 全てのカテゴリでw/o oracleのbem中

def main():
    # テストではaircraftカテゴリで実行
    category = "aircraft"
    category_dir = get_category_dir(category)
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)
    wikipedia_dir = f"{category_dir}/wikipedia"
    entity_id = "Q1019851"

    logger.info("Start generate_qa_by_entity ...")

    # ファイルから変数を取得せず、ベタ書きする場合はこちらに記述
    # entity_id = ""
    
    # これを行う場合はファイル保存以外はgenerate_qaと同様の処理をしている
    gpt_output = generate_qa_by_entity(entity_id, id_to_name, wikipedia_dir)
    # print("gpt_output")
    # print(gpt_output)
    # print()
    

    # ここで並列処理で高速化するためにsplit
    logger.info("Start convert_text_to_dict_by_entity ...")
    
    entity_to_qas = {}
    qas = convert_text_to_dict(gpt_output)
    entity_to_qas[entity_id] = qas

    # print("entity_to_qas")
    # print(entity_to_qas)
    # print()


    # CAUTION: ここから先はsplitごとに保存されたqaファイルがあることを前提
    logger.info("Start rephrase_questions_by_entity ...")

    for i, entity_id in tqdm(enumerate(entity_to_qas)):
        entity_to_qas[entity_id] = rephrase_questions_by_entity(entity_to_qas[entity_id])
        # print(entity_to_qas[entity_id])
    # print()


    logger.info("Start mask_entity_name_by_entity ...")
    for i, entity_id in tqdm(enumerate(entity_to_qas)):
        entity_to_qas[entity_id] = mask_questions_by_entity(entity_to_qas[entity_id], category, id_to_name, entity_id)
    #     print(entity_to_qas[entity_id])
    # print()
    

    logger.info("Start answer_by_entity ...")

    with open(f"{category_dir}/wikidata_filtered.json") as f:
        wikidata = json.load(f)
    wikipedia_dir = get_article_dir(category)
    with open(f"{category_dir}/predicted_ids.json") as f:
        predicted_ids = json.load(f)

    patterns = [
        {"name": False, "article": False, "relations": False, "confidence": False},
        {"name": True, "article": False, "relations": False, "confidence": False}, 
        {"name": True, "article": True, "relations": False, "confidence": False}, 
        {"name": True, "article": False, "relations": True, "confidence": False}, 
        {"name": True, "article": True, "relations": True, "confidence": False}, 
        # {"name": True, "article": True, "relations": True, "confidence": True}, 
    ]

    entity_to_qas[entity_id] = answer_by_entity(category, entity_id, qas, id_to_name, wikidata, wikipedia_dir, predicted_ids, patterns, mode="oracle")
    
    with open(f"{category_dir}/qa_test.json", 'w') as f:
        json.dump(entity_to_qas, f, indent=2)

    logger.info("Finish")

if __name__ == "__main__":
    main()