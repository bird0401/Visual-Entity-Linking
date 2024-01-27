import openai
import json, os
from utils.util import *

import traceback

from dotenv import load_dotenv
load_dotenv()
openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

import logging
import logging.config

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
def answer_by_categories(categories, patterns, mode="oracle", start_index=0, end_index=5000):
    patterns_str = ",".join([get_label(pattern) for pattern in patterns])
    logger.info(f"patterns: {patterns_str}")

    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qas_{start_index}.json") as f:
            qas = json.load(f) 
        # with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
        #     id_to_name = pickle.load(f)
        with open(f"{category_dir}/id_to_name.json") as f:
            id_to_name = json.load(f)
        with open(f"{category_dir}/wikidata_filtered.json") as f:
            wikidata = json.load(f)
        with open(f"{category_dir}/predicted_ids.json") as f:
            predicted_ids = json.load(f)

        # for entity_id in ["Q47309330"]:
        ids = list(qas.keys())
        logger.info(f"len(ids), start_index, end_index: {len(ids)}, {start_index}, {end_index}")
        # for i, entity_id_question in enumerate(ids):
        for i, entity_id_question in enumerate(ids[start_index:end_index]):
            if mode == "oracle":
                entity_id_predict = entity_id_question
            elif mode == "pred":
                if entity_id_question in predicted_ids:
                    entity_id_predict = predicted_ids[entity_id_question]
                else:
                    logger.info(f"Predicted id for {entity_id_question} is not found.")
                    continue
            
            if not entity_id_predict in id_to_name or not id_to_name[entity_id_predict]:
                logger.info(f"Name for {entity_id_question} is not found.")
                continue
            # pred modeで予測したidが正しい場合は、oracleで予測したものと被り、bemの際にはそちらを参照すれば良いため、スキップ
            if mode == "pred" and entity_id_predict == entity_id_question:
                logger.info(f"Skip because {entity_id_question} is oracle.")
                continue
            if not entity_id_predict in wikidata or not "text" in wikidata[entity_id_predict] or not wikidata[entity_id_predict]["text"]:
                logger.info(f"Relations for {entity_id_question} is not found.")
                continue
        
            wikidata_text = customize_relations(wikidata[entity_id_predict]["text"])
        
            if not wikidata_text: # TODO: previously delete wikidata text without sentences
                logger.info(f"Relations for {entity_id_question} is empty.")
                continue
            if not os.path.isfile(f"{category_dir}/wikipedia/{entity_id_predict}.txt"):
                logger.info(f"Article for {entity_id_question} is not found.")
                continue

            with open(f"{category_dir}/wikipedia/{entity_id_predict}.txt") as f:
                wikipedia_article = f.read()
            wikipedia_article = customize_text(wikipedia_article)

            if not wikipedia_article:
                logger.info(f"Article for {entity_id_question} is empty.")
                continue

            logger.info(f"Answering questions for {entity_id_question} using predicted id: {entity_id_predict}. ({i+1}/{len(qas)})")

            for i, qa in enumerate(qas[entity_id_question]):
                if not "Q_rephrase_mask" in qa or not qa["Q_rephrase_mask"]:
                    logger.info(f"Q_rephrase_mask is not found.")
                    continue
                if not "A" in qa or not qa["A"]:
                    logger.info(f"Answer is not found.")
                    continue

                # tasks = []
                for pattern in patterns:
                    key = f"{get_label(pattern)}_pred" if mode == "pred" else get_label(pattern)
                    if not key in qa:
                        qa[key] = {}

                    # 既に回答が存在する場合はスキップ
                    if qa[key]:
                        # logger.info(f"Skip because already answered to {entity_id_question}[{i}]['{get_label(pattern)}']")
                        logger.info(f"Skip because already answered to {entity_id_question}[{i}]['{key}']")
                        continue

                    qa[key]["A"] = answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text)
                
                # 非同期処理で実装しようとした時の名残一応残しておいているが、削除しても良い。
                #     tasks.append(answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text))
                # tasks = [answer(pattern, qa["Q_rephrase_mask"], category, id_to_name[entity_id_predict], wikipedia_article, wikidata_text) for pattern in patterns]
                # results = await asyncio.gather(*tasks)
                # for i, pattern in enumerate(patterns):
                #     qa[get_label(pattern)]["A"] = results[i]

        # patterns_str = "_".join([get_label(pattern) for pattern in patterns])
        # with open(f"{category_dir}/qas_{start_index}_{patterns_str}_{mode}.json", 'w') as f:
        with open(f"{category_dir}/qas_{start_index}_{mode}.json", 'w') as f:
            json.dump(qas, f, indent=2)

def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # answer_by_categories(categories)

if __name__ == "__main__":
    main()