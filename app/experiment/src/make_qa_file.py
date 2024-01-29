import sys
sys.path.append("utils")

from generate_qa import generate_qa_by_category
from convert_qa_text_to_json import convert_text_to_dict_by_category
from mask_question import mask_questions_by_category
from rephrase_question import rephrase_questions_by_category

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


# 8時間で5000エンティティが目安

def main():
    # categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]

    category = sys.argv[1] # "aircraft"
    mode = sys.argv[2] # gen, convert, ans
    
    # エンティティ数が多いものに関しては、並列処理って高速化を図る
    start_idx = int(sys.argv[3])
    end_idx = int(sys.argv[4])

    # # For test
    # start_idx = 0
    # end_idx = 3


    if mode == "gen":
        logger.info("Start generate_qa_by_categories ...")
        # idをファイル名として保存するため、splitごとにファイルを上書き保存することはない
        generate_qa_by_category(category, start_idx, end_idx)
    
    elif mode == "conv":
        # 重要: ここから先はsplitごとに上書き保存しないように、出力ファイルをqa_{start_idx}.jsonとし、最後に結合する
        # generate_qa_by_categoriesで生成したgpt-3_output上のファイルを参照し、それぞれの分割ごとにqa_{start_idx}.jsonとして出力
        logger.info("Start convert_text_to_dict_by_categories ...")
        convert_text_to_dict_by_category(category, start_idx, end_idx)

    elif mode == "reph":
        # CAUTION: ここから先はsplitごとに保存されたqaファイルがあることを前提としている
        logger.info("Start rephrase_questions_by_categories ...")
        rephrase_questions_by_category(category, start_idx, end_idx)
        
    elif mode == "mask":
        logger.info("Start mask_entity_name_by_categories ...")
        mask_questions_by_category(category, start_idx,end_idx)

    logger.info("Finish")


if __name__ == "__main__":
    main()
