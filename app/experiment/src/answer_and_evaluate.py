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

# predicted_id_and_confidences:
# {"indices": [[27, 3, 5, 26, 28, 14, 20, 25, 16, 10, 13, 21, 0, 33, 4, 2, 6, 1, 19, 29], [27, 5, 3, 26, 25, 14, 32, 4, 10, 33, 16, 9, 28, 12, 6, 23, 22, 2, 20, 13], [27, 5, 26, 3, 32, 16, 25, 33, 14, 9, 8, 4, 28, 22, 2, 29, 23, 10, 12, 6], [27, 25, 5, 32, 3, 14, 26, 16, 33, 4, 22, 24, 10, 9, 13, 23, 2, 28, 15, 6], [27, 5, 3, 26, 32, 14, 33, 25, 16, 4, 29, 24, 22, 9, 10, 23, 12, 13, 30, 1], [27, 3, 5, 26, 25, 16, 32, 9, 33, 12, 14, 4, 8, 15, 29, 28, 10, 19, 22, 23], [27, 32, 25, 5, 3, 26, 14, 4, 23, 9, 24, 33, 16, 2, 28, 29, 10, 22, 19, 12], [27, 3, 5, 32, 25, 26, 33, 14, 16, 28, 4, 22, 24, 10, 8, 23, 29, 12, 9, 1], [27, 5, 3, 26, 25, 4, 32, 33, 9, 22, 14, 16, 6, 10, 23, 13, 2, 29, 15, 28], [27, 5, 26, 32, 3, 25, 14, 33, 9, 16, 24, 4, 10, 8, 29, 13, 23, 6, 22, 12], [27, 3, 26, 5, 14, 32, 33, 25, 23, 10, 16, 1, 4, 24, 22, 6, 9, 12, 28, 13]], "confidences": [[0.09066298604011536, 0.06920187175273895, 0.06450272351503372, 0.05599862337112427, 0.05571328476071358, 0.05272199586033821, 0.05045003071427345, 0.050038255751132965, 0.04790296033024788, 0.044799499213695526, 0.04456270486116409, 0.04370317980647087, 0.04350675269961357, 0.04333929345011711, 0.04215420037508011, 0.04195605590939522, 0.041692525148391724, 0.04110674187541008, 0.038956623524427414, 0.037029676139354706], [0.25518715381622314, 0.13702481985092163, 0.11815229803323746, 0.07484743744134903, 0.04804055392742157, 0.04073666036128998, 0.03706292435526848, 0.031423043459653854, 0.02939417213201523, 0.02926037646830082, 0.026614617556333542, 0.024812044575810432, 0.02257551997900009, 0.021253379061818123, 0.01961371675133705, 0.018416637554764748, 0.017128871753811836, 0.016895201057195663, 0.01583286002278328, 0.015727780759334564], [0.4982847571372986, 0.10432770848274231, 0.0898035541176796, 0.046714819967746735, 0.04252126067876816, 0.04113411158323288, 0.03525322675704956, 0.028764402493834496, 0.014186183921992779, 0.012926560826599598, 0.011136804707348347, 0.01016464363783598, 0.00922241248190403, 0.008944051340222359, 0.00869782641530037, 0.008313407190144062, 0.008095784112811089, 0.007914832793176174, 0.0073166703805327415, 0.006276991218328476], [0.9067637920379639, 0.015101614408195019, 0.012999466620385647, 0.012919238768517971, 0.012056028470396996, 0.010169131681323051, 0.006388470530509949, 0.004093109630048275, 0.0032774959690868855, 0.003258358919993043, 0.0020745510701090097, 0.001770844915881753, 0.0016171472379937768, 0.0014367062831297517, 0.0013935177121311426, 0.001365235890261829, 0.0008585799369029701, 0.0008569455239921808, 0.000833367754239589, 0.0007662864518351853]

def fetch_variables_for_ansewring(mode, gt_entity_id, wikidata, wikipedia_dir, predicted_id_and_confidences, top-k):
    if mode == "oracle":
        entity_id = gt_entity_id
        confidence = 1.0
    # TODO: fix this to match ml output
    # in actual ml outout, it predicts to multiple images, but here we only use index 0 results
    # TODO: temporary, extract only top-1 entity and confidence
    elif mode == "pred":
        i_th = 0
        top_k = 1
        entity_id = predicted_id_and_confidences["indices"][i_th][top_k-1]
        confidence = predicted_id_and_confidences["confidences"][i_th][top_k-1]
    
    logger.info(f"gt_entity_id: {gt_entity_id}, entity_id: {entity_id}, confidence: {confidence}")

    wikidata_rdf_text = customize_relations(wikidata[entity_id]["text"])
    if not wikidata_rdf_text:
        logger.info("Wikidata is None")
        raise

    article = exploit_customized_article(entity_id, wikipedia_dir)
    if not article:
        logger.info(f"Article is None")
        raise

    return entity_id, confidence, wikidata_rdf_text, article


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
    # with open(f"{category_dir}/predicted_ids.json") as f:
    #     predicted_ids = json.load(f)
    with open(f"{category_dir}/weights/{weight_id}/id_indices_confidences_epoch10.json") as f:
        gt_id_to_predicted_id_and_confidences = json.load(f)    

    return entity_to_qas_path, entity_to_qas, id_to_name, wikidata, wikipedia_dir, gt_id_to_predicted_id_and_confidences


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
    

def answer_by_entity(category, gt_entity_id, qas, id_to_name, wikidata, wikipedia_dir, predicted_id_and_confidences, mode):

    entity_id, wikidata_rdf_text, article = fetch_variables_for_ansewring(mode, gt_entity_id, wikidata, wikipedia_dir, predicted_id_and_confidences)

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
    

# TODO: 
# - top-kでも対応するようにする(top1 preference)
    # - in ml side, we should make it output top-k entities and their confidence scores
    # - in this side, we should make it top-k information as gpt-3 input. 
# - if we do it, gpt-3 input token limitation is a problem
# - generate qa, answer, bem, and evaluate all entities across all categories

# 1jobあたり5000エンティティくらい(処理時間の見積もりは約8時間)が限界
def answer_by_category(category, mode="oracle", start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    entity_to_qas_path, entity_to_qas, id_to_name, wikidata, wikipedia_dir, gt_id_to_predicted_id_and_confidences = fetch_variables_by_category(category, start_idx, end_idx)
    logger.info(f"len(entity_to_qas): {len(entity_to_qas)}")
    # デバッグ用
    # print("entity_to_qas_path")
    # print(entity_to_qas_path)
    # print("entity_to_qas")
    # print(entity_to_qas)
    for i, gt_entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"Answer questions of {gt_entity_id}, idx: {start_idx+i}")
        try:             
            entity_to_qas[gt_entity_id] = answer_by_entity(category, gt_entity_id, entity_to_qas[gt_entity_id], id_to_name, wikidata, wikipedia_dir, gt_id_to_predicted_id_and_confidences[gt_entity_id], mode)
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
