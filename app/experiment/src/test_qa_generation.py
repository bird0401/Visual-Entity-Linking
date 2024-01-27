# import sys
# sys.path.append("utils")

from config import *
from util import *
from generate_qa import *
from convert_to_json import *
# from rephrase_questions import *
# from masking_by_category import *
# from answer import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# TODO: もっと依存性がなく簡単に実行できるようにする
# TODO: 一部のQAはmaskingなど一部かけている影響によって、答えが得られていないため、現在は精度を試す時にそれらは除外している
# TODO: 実際にこのファイルを利用してテストしたことがないので、ひと段落した後に実際に実行してみる
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
    

    logger.info("Start generate_qa_by_categories ...")

    entity_id = "Q1019851"
    # これを行う場合はファイル保存以外はgenerate_qaと同様の処理をしている
    entity_name, article = exploit_info_for_gpt(entity_id, id_to_name, wikipedia_dir)
    # ファイルから変数を取得せず、ベタ書きする場合はこちらに記述
    # entity_name = ""
    # article = ""
    output = gpt_request(entity_name, article)
    print(output)

    
    # generate_qa_by_categoriesで生成したgpt-3_output上のファイルを参照し、それぞれの分割ごとにqa_{start_index}.jsonとして出力
    logger.info("Start convert_text_to_dict_by_categories ...")
    
    output_dict_list = convert_text_to_dict(output)

    # CAUTION: ここから先はsplitごとに保存されたqaファイルがあることを前提
    logger.info("Start rephrase_questions_by_categories ...")

    # questions = []
    # for qa in output_dict_list:
    #     questions.append(qa[key])

    questions_text = "\n".join(output_dict_list)
    # rephrase_questions_by_categories(categories, start_index, end_index)
    questions_rephrased = rephrase_questions(questions_text)
    questions_rephrased_list = questions_rephrased.split("\n")
    
    # logger.info("Start mask_entity_name_by_categories ...")
    # mask_entity_name_by_categories(categories, start_index,end_index)
        
    
    # # elif mode == "ans":
    # #     logger.info("Start answer_by_categories ...")
    # #     if len(sys.argv) >= 5:
    # #         answer_by_categories(categories, patterns, mode=ans_mode, start_index=start_index, end_index=end_index)
    # #     else:
    # #         answer_by_categories(categories, patterns, mode=ans_mode)
    

    logger.info("Finish")

if __name__ == "__main__":
    main()