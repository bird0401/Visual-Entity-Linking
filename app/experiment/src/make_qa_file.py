import sys
sys.path.append("utils")

from generate_qa import generate_qa_by_categories
from convert_to_json import convert_text_to_dict_by_categories
from masking_by_category import mask_entity_name_by_categories
from rephrase_questions import rephrase_questions_by_categories
from answer import answer_by_categories

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

def main():
    categories = ["bird"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    logger.info("Start generate_qa_by_categories ...")
    generate_qa_by_categories(categories)
    logger.info("Start convert_text_to_dict_by_categories ...")
    convert_text_to_dict_by_categories(categories)
    logger.info("Start rephrase_questions_by_categories ...")
    rephrase_questions_by_categories(categories)
    logger.info("Start mask_entity_name_by_categories ...")
    mask_entity_name_by_categories(categories)
    logger.info("Start answer_by_categories ...")
    answer_by_categories(categories)
    logger.info("Finish")

if __name__ == "__main__":
    main()