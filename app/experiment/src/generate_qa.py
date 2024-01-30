import os, textwrap, traceback
from tqdm import tqdm
from util import *
from config import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def create_messages_for_generate_qa(entity_name, article):

    messages_for_generate_qa = [
        {"role": "system", "content": "You are a helpful annotator of wikipedia articles."},
        {"role": "user", "content": textwrap.dedent(f"""
            Generate ten pairs of QA based on the article. Each question must contain the entity name. Use the following format:
            Q: Where was Thomas Flögel born?
            A: Vienna.
            
            Q: Which club did Thomas Flögel play for in Scotland?
            A: Heart of Midlothian.
            
            Q: How many league titles did Thomas Flögel win with Austria Wien?
            A: Three consecutive league titles.
            
            Q: Which club did Thomas Flögel return to after playing abroad?
            A: FK Austria.
            
            Q: What position did Thomas Flögel play during his time with Hearts?
            A: He played in every outfield position.
            """)},
        {"role": "assistant", "content": f"Entity name: {entity_name}"},
        {"role": "assistant", "content": f"Article:\n{article}"},
    ]

    return messages_for_generate_qa


def generate_qa_by_entity(entity_id, id_to_name, wikipedia_dir):
    entity_name = id_to_name[entity_id]
    
    article = exploit_customized_article(entity_id, wikipedia_dir)
    if not article:
        logger.info("article is None")
        return
    
    messages = create_messages_for_generate_qa(entity_name, article)
    gpt_output = gpt_request(messages)   
    return gpt_output


# カテゴリごとにファイルを管理している都合上、カテゴリ単位で実行
def generate_qa_by_category(category, start_idx=0, end_idx=5000):
    logger.info(f"category: {category}")
    category_dir = get_category_dir(category)

    with open(f"{category_dir}/ids.json") as f:
        entity_ids = json.load(f)

    # カテゴリごとにそのカテゴリのidと名前の対応付け用ファイルが存在
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)

    output_dir = get_gpt_output_dir(category)
    wikipedia_dir = get_article_dir(category)

    # 既存の出力先ディレクトリが存在する場合は手動で削除してから実行する必要がある
    os.makedirs(output_dir, exist_ok=False)

    logger.info(f"len(entity_ids), start_idx, end_idx: {len(entity_ids)}, {start_idx}, {end_idx}")
    for i, entity_id in tqdm(enumerate(entity_ids[start_idx:end_idx])):
        logger.info(f"Generate questions for {entity_id}, idx: {start_idx+i}")
        
        # テスト用
        # if os.path.exists(f"{output_dir}/{entity_text_file}"):
        #     logger.info(f"Skip {entity_id} because already generated")
        #     continue

        # gptによる生成
        try:
            gpt_output = generate_qa_by_entity(entity_id, id_to_name, wikipedia_dir)
        
            # 出力の保存
            if not gpt_output:
                logger.info(f"Skip {entity_id} because output is empty")
            with open(f"{output_dir}/{entity_id}.txt", 'w') as f:
                f.write(gpt_output)

        except Exception:
            traceback.print_exc()


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        generate_qa_by_category(category, start_idx=0, end_idx=3)


if __name__ == "__main__":
    main()

