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

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) 


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


def rephrase_questions_by_entity(entity_id, qas):
    questions = []
    for qa in qas:
        questions.append(qa["Q"])
    questions_text = "\n".join(questions)
    messages = create_messages_for_repharase_questions(questions_text)
    questions_rephrased = gpt_request(messages)
    questions_rephrased_list = questions_rephrased.split("\n")
    return questions_rephrased_list

def rephrase_questions_by_category(category, start_idx=0, end_idx=5000):
        logger.info(f"category: {category}")
        category_dir = get_category_dir(category)
        qa_path = get_save_path(category_dir, start_idx, end_idx)
        
        with open(qa_path) as f:
            entity_to_qas = json.load(f)
        
        for i, entity_id in tqdm(enumerate(entity_to_qas)):
            logger.info(f"Paraphrase questions for {entity_id}, idx: {start_idx+i}")
            try:
                # TODO: ここでmergeするのは、gpt-3の入力に対して、一つの文章として入力した方がgptへのリクエスト数を減らせることと、あるエンティティに関する複数のQAをバッチ処理できるため

                questions_rephrased_list = rephrase_questions_by_entity(entity_id, entity_to_qas[entity_id])
                
                questions_merge = merge_text(entity_to_qas[entity_id], "Q")
                
                # 既にパラフレーズされている場合はスキップ

                cnt = 0
                for i, qa in enumerate(entity_to_qas[entity_id]):
                    if "Q_rephrase" in qa and qa["Q_rephrase"]:
                        cnt += 1
                # print(f"cnt, len(entity_to_qas[entity_id]): {cnt}, {len(entity_to_qas[entity_id])}")
                if cnt == len(entity_to_qas[entity_id]):
                    logger.info(f"Skip {entity_id} because all questions are already paraphrased")
                    continue    
                                
                messages = create_messages_for_repharase_questions(questions_merge)
                questions_rephrased = gpt_request(messages)
                questions_rephrased_list = questions_rephrased.split("\n")
                for i, qa in enumerate(entity_to_qas[entity_id]):
                    qa["Q_rephrase"] = questions_rephrased_list[i]
            except Exception as e:
                logger.error(f"entity_id: {entity_id}")
                logger.error(e)
        with open(f"{category_dir}/entity_to_qas_{start_idx}.json", 'w') as f:
            json.dump(entity_to_qas, f, indent=2)


# TODO: attach tqdm overall
def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        rephrase_questions_by_category(category)


if __name__ == "__main__":
    main()
