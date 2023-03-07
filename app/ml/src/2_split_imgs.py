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


def export_imgs(row, category_dir):
    assert type(row) == pd.Series
    assert type(category_dir) == str
    src = row["path"]
    assert os.path.exists(src), f"{src} does not exist"
    if row["kfold"] == 0:
        dst = f"{category_dir}/val/{row['wikidata_id']}/{row['file_name']}"
    else:
        dst = f"{category_dir}/train/{row['wikidata_id']}/{row['file_name']}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    assert os.path.exists(dst), f"{dst} does not exist"


def main():
    data_dir = "../../../data/clean"
    # dir_names = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    dir_names = ["us_politician"]
    for dir_name in dir_names:
        category_dir = f"{data_dir}/{dir_name}"
        logger.info(f"category_dir: {category_dir}")

        df_train = pd.read_csv(f"{category_dir}/csv/train.csv")
        assert len(df_train) > 0, "df_train is empty"
        logger.info(f"df_train: {df_train.shape}")

        for _, row in tqdm(df_train.iterrows()):
            export_imgs(row, category_dir)


if __name__ == "__main__":
    main()
