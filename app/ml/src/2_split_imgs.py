import os, shutil
from tqdm import tqdm
import pandas as pd

import logging
import logging.config
from yaml import safe_load


with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def export_imgs(row, category_dir, is_train):
    assert type(row) == pd.Series
    assert type(category_dir) == str
    src = row["path"]
    assert os.path.exists(src), f"{src} does not exist"
    if is_train:
        if row["kfold"] == 0:
            dst = f"{category_dir}/val/{row['wikidata_id']}/{row['file_name']}"
        else:
            dst = f"{category_dir}/train/{row['wikidata_id']}/{row['file_name']}"
    else:
        dst = f"{category_dir}/test/{row['wikidata_id']}/{row['file_name']}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    assert os.path.exists(dst), f"{dst} does not exist"

def main():
    data_dir = "../../../data/clean"
    dir_names = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # dir_names = ["athlete"]
    is_train = False
    for dir_name in dir_names:
        category_dir = f"{data_dir}/{dir_name}"
        logger.info(f"category_dir: {category_dir}")
        df = pd.read_csv(f"{category_dir}/csv/train.csv") if is_train else pd.read_csv(f"{category_dir}/csv/test.csv")
        assert len(df) > 0, "df is empty"
        logger.info(f"df: {df.shape}")

        for _, row in tqdm(df.iterrows(), total=len(df)):
            export_imgs(row, category_dir, is_train)
        
        logger.info(f"num of images: {len(df)}")
        print()

if __name__ == "__main__":
    main()
