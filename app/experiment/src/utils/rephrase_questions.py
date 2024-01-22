import openai
import os, json, textwrap
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

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def rephrase_questions(text):
    try:
        messages=[
            {"role": "system", "content": "You are a helpful annotator of sentences."},
            {"role": "user", "content": textwrap.dedent(f"""
                In this task, please paraphrase sentences. See the examples below.

                Before paraphrasing:
                When was Azzeddine Toufiqui born?
                Which position does Azzeddine Toufiqui play in football?
                Which club did Azzeddine Toufiqui join in 2015?
                In which league did Azzeddine Toufiqui's former club Caen play?
                When did Azzeddine Toufiqui make his professional debut?

                After paraphrasing:
                What is the birth date of Azzeddine Toufiqui?
                What is Azzeddine Toufiqui's football position?
                In 2015, which team did Azzeddine Toufiqui become a member of?
                Which league did Caen, Azzeddine Toufiqui's previous club, compete in?
                When did Azzeddine Toufiqui first play professionally?

                Based on the above examples, please paraphrase following sentences.
                """)},
            {"role": "assistant", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
        return response.choices[0]["message"]["content"]
    except Exception as e:
        logger.error(f"text: {text}")
        logger.error(e)

def rephrase_questions_by_categories(categories, start_idx=0, end_idx=5000):
    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        
        with open(f"{category_dir}/qas_{start_idx}.json") as f:
            qas = json.load(f)
        ids = list(qas.keys())
        # ids = ["Q25172100"]
        # for i, entity_id in enumerate(ids[start_idx:end_idx]):
        for i, entity_id in enumerate(ids):
            logger.info(f"Paraphrase questions for {entity_id} ({i+1}/{len(qas)})")
            try:
                questions_merge = merge_text(qas[entity_id], "Q")
                
                # 既に全ての質問がパラフレーズされている場合はスキップ
                cnt = 0
                for i, qa in enumerate(qas[entity_id]):
                    if "Q_rephrase" in qa and qa["Q_rephrase"] != "":
                        cnt += 1
                # print(f"cnt, len(qas[entity_id]): {cnt}, {len(qas[entity_id])}")
                if cnt == len(qas[entity_id]):
                    logger.info(f"Skip {entity_id} because all questions are already paraphrased")
                    continue    
                                
                questions_rephrased = rephrase_questions(questions_merge)
                questions_rephrased_list = questions_rephrased.split("\n")
                for i, qa in enumerate(qas[entity_id]):
                    qa["Q_rephrase"] = questions_rephrased_list[i]
            except Exception as e:
                logger.error(f"entity_id: {entity_id}")
                logger.error(e)
        with open(f"{category_dir}/qas_{start_idx}.json", 'w') as f:
            json.dump(qas, f, indent=2)

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    rephrase_questions_by_categories(categories)

if __name__ == "__main__":
    main()

