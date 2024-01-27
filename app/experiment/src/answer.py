import json, os
from util import *
from config import *

from tqdm import tqdm

import logging
import logging.config

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")



# gpt-3へのリクエストを非同期に変更しても処理速度は変化しなかったことと、retryは利用できなくなるので、ここは非同期にはしない
# 代わりに、それぞれのpatternごとに実行することで、処理速度を改善する
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def answer(info, question, category, entity_name, wikipedia_article, wikidata_text_by_relation):
    messages = []
    if info["name"] and entity_name:
        # カテゴリ名で置換されているところをエンティティ名に戻す
        messages.append({"role": "assistant", "content": f"Name of the {category}: {entity_name}"})
        # TODO: こちらの方が良いのではないか
        # messages.append({"role": "assistant", "content": f"This {category} is {entity_name}"})
    if info["article"] and wikipedia_article:
        messages.append({"role": "assistant", "content": f"Article:\n{wikipedia_article}"})
    if info["relations"] and wikidata_text_by_relation:
        messages.append({"role": "assistant", "content": f"Relations:\n{wikidata_text_by_relation}"})
    messages.append({"role": "system", "content": f"You are a helpful QA bot."})
    if question:
        messages.append({"role": "user", "content": f"Please answer the following question.\nQuestion: {question}"})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    return response.choices[0]["message"]["content"]

# TODO: top-kでも対応するようにする
# TODO: 書き終わったら文字数を測る
# 1jobあたり5000エンティティくらい(処理時間の見積もりは約8時間)が限界
def answer_by_category(category, patterns, mode="oracle", start_idx=0, end_idx=5000):
    patterns_str = ",".join([get_label(pattern) for pattern in patterns])
    logger.info(f"patterns: {patterns_str}")

    logger.info(f"category: {category}")
    category_dir = get_category_dir(category)
    entity_to_qas_path = get_entity_tp_qas_path(category_dir, start_index, end_index)
    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f) 
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)
    with open(f"{category_dir}/wikidata_filtered.json") as f:
        wikidata = json.load(f)
    with open(f"{category_dir}/predicted_ids.json") as f:
        predicted_ids = json.load(f)
    logger.info(f"len(entity_to_qas): {len(entity_to_qas)}")

    for i, gt_entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"Answer questions of {gt_entity_id}, idx: {start_idx+i}")
        try: 
            if mode == "oracle":
                entity_id_predict = gt_entity_id
            elif mode == "pred":
                if gt_entity_id in predicted_ids:
                    entity_id_predict = predicted_ids[gt_entity_id]
            
            # pred modeで予測したidが正しい場合は、oracleで予測したものと被り、bemの際にはそちらを参照すれば良いため、スキップ
            # 時間がなかったので以前の処理ではスキップしていたが、評価の方の実装が面倒になるので、重複はするもののこれも回答するようにした
            # if mode == "pred" and entity_id_predict == gt_entity_id:
            #     logger.info(f"Skip because {gt_entity_id} is oracle.")
            #     continue
            
            wikidata_text = customize_relations(wikidata[entity_id_predict]["text"])

            with open(f"{category_dir}/wikipedia/{entity_id_predict}.txt") as f:
                wikipedia_article = f.read()
            wikipedia_article = customize_text(wikipedia_article)

            # This error can not be caught by error handling
            if not wikipedia_article:
                logger.info(f"Article for {gt_entity_id} is empty.")
                continue

            logger.info(f"Answering questions for {gt_entity_id} using predicted id: {entity_id_predict}. ({i+1}/{len(entity_to_qas)})")

            for i, qa in enumerate(entity_to_qas[gt_entity_id]):
                try:
                    for pattern in patterns:
                        key = f"{get_label(pattern)}_pred" if mode == "pred" else get_label(pattern)
                        if not key in qa:
                            qa[key] = {}

                        # 既に回答が存在する場合はスキップ
                        if qa[key]:
                            # logger.info(f"Skip because already answered to {gt_entity_id}[{i}]['{get_label(pattern)}']")
                            logger.info(f"Skip because already answered to {gt_entity_id}[{i}]['{key}']")
                            continue

                        qa[key]["A"] = answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text)
                except Exception:
                    traceback.1print_exc()
                    continue
                
                # 非同期処理で実装しようとした時の名残一応残しておいているが、削除しても良い。
                #     tasks.append(answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text))
                # tasks = [answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text) for pattern in patterns]
                # results = await asyncio.gather(*tasks)
                # for i, pattern in enumerate(patterns):
                #     qa[get_label(pattern)]["A"] = results[i]
        except Exception:
            traceback.print_exc()
            continue

    # patterns_str = "_".join([get_label(pattern) for pattern in patterns])
    # with open(f"{category_dir}/qas_{start_index}_{patterns_str}_{mode}.json", 'w') as f:
    with open(entity_to_qas_path, 'w') as f:
        json.dump(entity_to_qas_path, f, indent=2)


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        answer_by_category(category)


if __name__ == "__main__":
    main()