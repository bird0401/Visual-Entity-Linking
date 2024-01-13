import glob, random, shutil, os

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# 注意: pythonスクリプトより、linuxコマンドの方が高速なので、ここの処理はlinuxコマンドで行う
# 注意: そもそもコピーを行うより、圧縮ファイルを作成し、適宜解凍する方が良い
# 圧縮で用いるコマンド
# tar -czvf clean_backup.tar.gz clean

# clean_dirの中身をコピーし、clean_backupに保存する
def copy_images_by_id(clean_dir):
    logger.info(f"clean_dir: {clean_dir}")


# デバッグ用に、ディレクトリをコピーする
def main():
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        logger.info(category)
        copy_
    path_ids = glob.glob("../data/athlete/imgs/Q*")  # change directory name by category
    path_ids_sample = random.sample(path_ids, 10)
    dst_dir = "../data/athlete_debug/imgs"
    try:
        os.makedirs(dst_dir, exist_ok=True)
    except FileExistsError:
        logger.info("exists")
    for src_dir in path_ids_sample:
        logger.info(src_dir)
        id_sample = src_dir.split("/")[-1]
        shutil.copytree(src_dir, f"{dst_dir}/{id_sample}")


if __name__ == "__main__":
    main()
