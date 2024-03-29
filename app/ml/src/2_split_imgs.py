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

# dfの内容に合わせて、train, test用のディレクトリを作成し、それらに振り分ける
# 注意: 画像枚数5枚以下のidに関してはcsv上に記されないことにより、それらは移動せずに残る
def export_imgs(row, category_dir, mode):
    assert type(row) == pd.Series
    assert type(category_dir) == str
    src = row["path"]
    assert os.path.exists(src), f"{src} does not exist"
    if mode == "train":
        dst = f"{category_dir}/train/{row['wikidata_id']}/{row['file_name']}"
        # valを使わなくなったため、一旦コメントアウト
        # if row["kfold"] == 0:
        #     dst = f"{category_dir}/val/{row['wikidata_id']}/{row['file_name']}"
        # else:
        #     dst = f"{category_dir}/train/{row['wikidata_id']}/{row['file_name']}"
    else:
        dst = f"{category_dir}/test/{row['wikidata_id']}/{row['file_name']}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # shutil.copyfile(src, dst)
    shutil.move(src, dst)
    assert os.path.exists(dst), f"{dst} does not exist"


# Change
# - data_dir
def main():
    data_dir = "../../../data"
    # categories = ["aircraft"]
    categories = ["athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        logger.info(f"category_dir: {category_dir}")
        # TODO: 危険なのでコメントアウト。手動でdeleteすること
        # for mode in ["train", "val", "test"]:
            # if os.path.exists(f"{category_dir}/{mode}"):
            #     shutil.rmtree(f"{category_dir}/{mode}")
        for mode in ["train", "test"]:
            logger.info(f"mode: {mode}")
            df = pd.read_csv(f"{category_dir}/csv/{mode}.csv") 
            assert len(df) > 0, "df is empty"
            logger.info(f"df: {df.shape}")

            for _, row in tqdm(df.iterrows(), total=len(df)):
                export_imgs(row, category_dir, mode)
            
            logger.info(f"num of images: {len(df)}")
            print()

if __name__ == "__main__":
    main()
