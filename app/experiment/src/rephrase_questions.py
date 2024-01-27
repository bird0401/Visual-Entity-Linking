import openai
import os, json, textwrap
from util import *
from config import *
from tqdm import tqdm

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


def create_messages_for_repharase_questions(questions):

    messages_for_repharase_questions=[
        {"role": "system", "content": "You are a helpful annotator of sentences."},
        {"role": "user", "content": textwrap.dedent(f"""
            Like following examples,

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

            Paraphrase following sentences.
            """)},
        {"role": "assistant", "content": questions},
    ]

    return messages_for_repharase_questions


def rephrase_questions_by_entity(qas):
    # Skip if all questions are already paraphrased
    cnt = 0
    for i, qa in enumerate(qas):
        if "Q_rephrase" in qa and qa["Q_rephrase"]:
            cnt += 1
    if cnt == len(qas):
        logger.info(f"Skip because all questions are already paraphrased")
        return    

    questions_merge = merge_list_text(qas, "Q")
    messages = create_messages_for_repharase_questions(questions_merge)
    questions_rephrased = gpt_request(messages)
    questions_rephrased_list = questions_rephrased.split("\n")
    for i, qa in enumerate(qas):
        qa["Q_rephrase"] = questions_rephrased_list[i]
    return qas


def rephrase_questions_by_category(category, start_idx=0, end_idx=5000):
        logger.info(f"category: {category}")
        category_dir = get_category_dir(category)
        entity_to_qas_path = get_save_path(category_dir, start_idx, end_idx)
        
        with open(entity_to_qas_path) as f:
            entity_to_qas = json.load(f)
        
        for i, entity_id in tqdm(enumerate(entity_to_qas)):
            logger.info(f"Paraphrase questions for {entity_id}, idx: {start_idx+i}")
            try:
            # TODO: QAごとではなくエンティティごとに複数のQAを一気に処理するのは、gptへのリクエスト数を減らせるため
            # これで大丈夫かテスト
                entity_to_qas[entity_id] = rephrase_questions_by_entity(entity_to_qas[entity_id])
            except Exception as e:
                logger.error(e)

        with open(entity_to_qas_path) as f:
            json.dump(entity_to_qas_path, f, indent=2)


# TODO: 
# - attach tqdm overall
# - validate generated QA by gpt, because its output is not always correct
def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        rephrase_questions_by_category(category)


if __name__ == "__main__":
    main()
