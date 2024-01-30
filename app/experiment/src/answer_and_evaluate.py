import json
import sys
from util import *
from config import *

from tqdm import tqdm

import logging
import logging.config

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def fetch_variables_for_ansewring(mode, gt_entity_id, wikidata, wikipedia_dir, predicted_ids):
    if mode == "oracle":
        entity_id = gt_entity_id
    elif mode == "pred":
        entity_id = predicted_ids[gt_entity_id]
    logger.info(f"gt_entity_id: {gt_entity_id}, entity_id: {entity_id}")

    wikidata_rdf_text = customize_relations(wikidata[entity_id]["text"])
    if not wikidata_rdf_text:
        logger.info("Wikidata is None")
        raise

    article = exploit_customized_article(entity_id, wikipedia_dir)
    if not article:
        logger.info(f"Article is None")
        raise

    return entity_id, wikidata_rdf_text, article


def fetch_variables_by_category(category, start_idx, end_idx):
    category_dir = get_category_dir(category)
    entity_to_qas_path = get_entity_to_qas_path(category, start_idx, end_idx)
    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f) 
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)
    with open(f"{category_dir}/wikidata_filtered.json") as f:
        wikidata = json.load(f)
    wikipedia_dir = get_article_dir(category)
    with open(f"{category_dir}/predicted_ids.json") as f:
        predicted_ids = json.load(f)

    return entity_to_qas_path, entity_to_qas, id_to_name, wikidata, wikipedia_dir, predicted_ids


def create_messages_for_answer(pattern, category, question, entity_name, article, wikidata_rdf_text):
    messages = []
    try:
        if pattern["name"]:
            # カテゴリ名で置換されているところをエンティティ名に戻す
            # used
            # messages.append({"role": "assistant", "content": f"Name of the {category}: {entity_name}"})
            messages.append({"role": "assistant", "content": f"This {category} is {entity_name}"})
        if pattern["article"]:
            messages.append({"role": "assistant", "content": f"Article:\n{article}"})
        if pattern["relations"]:
            messages.append({"role": "assistant", "content": f"Relations:\n{wikidata_rdf_text}"})
        messages.append({"role": "system", "content": f"You are a helpful QA bot."})
        messages.append({"role": "user", "content": f"Please answer the following question.\nQuestion: {question}"})
        return messages
    except Exception:
        traceback.print_exc()
        return
    

def answer_by_entity(category, gt_entity_id, qas, id_to_name, wikidata, wikipedia_dir, predicted_ids, mode):

    entity_id, wikidata_rdf_text, article = fetch_variables_for_ansewring(mode, gt_entity_id, wikidata, wikipedia_dir, predicted_ids)

    for i, qa in enumerate(qas):
        try:
            for pattern in patterns:

                pattern_label = get_label(pattern)
                
                # 既に回答が存在する場合はスキップ
                # 現状は不必要に感じるのでコメントアウト
                # if f"A_{mode}_{pattern_label}" in qa[f"A_{mode}_{pattern_label}"]:
                #     logger.info(f"Skip because already answered to {entity_id}[{i}]['{pattern_label}']")
                #     continue
                
                messages_for_answer = create_messages_for_answer(pattern, category, qa["Q_rephrase_mask"], id_to_name[entity_id], article, wikidata_rdf_text)
                qa[f"A_{mode}_{pattern_label}"] = gpt_request(messages_for_answer)

        except Exception:
            traceback.print_exc()
            continue
    
    return qas
    

# TODO: top-kでも対応するようにする
# - in ml side, we should make it output top-k entities and their confidence scores
# - in this side, we should make it top-k information as gpt-3 input. 
    # - if we do it, gpt-3 input token limitation is a problem
# TODO: 書き終わったら文字数を測る
# 1jobあたり5000エンティティくらい(処理時間の見積もりは約8時間)が限界
def answer_by_category(category, mode="oracle", start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    entity_to_qas_path, entity_to_qas, id_to_name, wikidata, wikipedia_dir, predicted_ids = fetch_variables_by_category(category, start_idx, end_idx)
    logger.info(f"len(entity_to_qas): {len(entity_to_qas)}")
    # デバッグ用
    # print("entity_to_qas_path")
    # print(entity_to_qas_path)
    # print("entity_to_qas")
    # print(entity_to_qas)
    for i, gt_entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"Answer questions of {gt_entity_id}, idx: {start_idx+i}")
        try:             
            entity_to_qas[gt_entity_id] = answer_by_entity(category, gt_entity_id, entity_to_qas[gt_entity_id], id_to_name, wikidata, wikipedia_dir, predicted_ids, mode)
        except Exception:
            traceback.print_exc()
            continue

    with open(entity_to_qas_path, 'w') as f:
        json.dump(entity_to_qas, f, indent=2)


def calculate_accuracy(category, mode, start_idx, end_idx):
    entity_to_qas_bem_path = get_entity_to_qas_bem_path(category, start_idx, end_idx)
    with open(entity_to_qas_bem_path) as f:
        entity_to_qas_bem = json.load(f) 
    
    for pattern in patterns:
        pattern_label = get_label(pattern)

        total = 0
        correct = 0
        for entity_id, qas in entity_to_qas_bem.items():
            for qa in qas:
                if qa[f"A_{mode}_{pattern_label}_score"] >= 0.5:
                    correct += 1
                total += 1
        
        print(f"category: {category}")
        print(f"mode: {mode}")
        print(f"pattern: {pattern_label}")
        print(f"total: {total}")
        print(f"correct: {correct}")
        print(f"accuracy: {correct / total}")
        print()
    

def main():
    logger.info("Start answer_by_categories ...")

    # For test
    category = "aircraft" 
    start_idx = 0
    end_idx = 3
    mode = "oracle"
    
    # category = sys.argv[1] # "aircraft"
    # start_idx = int(sys.argv[2])
    # end_idx = int(sys.argv[3])
    # mode = sys.argv[4] # "oracle" or "pred"

    # step = "answer"
    step = "accuracy"
    logger.info(f"Start {step} ...")

    if step == "answer":
        answer_by_category(category, mode, start_idx, end_idx)

    # betweeen them, we should calculate bem score in bem.py on tensorflow container 

    elif step == "accuracy":
        calculate_accuracy(category, mode, start_idx, end_idx)


if __name__ == "__main__":
    main()
