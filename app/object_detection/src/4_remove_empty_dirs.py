import glob, shutil

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# TODO: clean_dirに行くタイミングがわからないので、確認しておく
def remove_crop_dirs(category, r_id_dirs):
    logger.info(f"category: {category}")
    data_dir = f"../../../data/clean"  # For cleaned data
    # data_dir = f"../../../data/origin" # For original data
    category_dir = f"{data_dir}/{category}"
    # category_dir = f"{data_dir}/{category}_debug" if is_debug else f"{data_dir}/{category}"
    wikidata_id_dirs = glob.glob(f"{category_dir}/images/clean/*")
    cnt = 0
    for wikidata_id_dir in wikidata_id_dirs:
        if len(glob.glob(f"{wikidata_id_dir}*.jpg")) == 0:
            shutil.rmtree(wikidata_id_dir)
            cnt += 1
    logger.info(f"Remove {cnt} dirs")
    print()

# TODO: 空のディレクトリを削除するためのものであるが、必要ないかも
# TODO: もし可能なら、MLの方で空の場合でも対処できるようにする。データセットに関する統計情報作成の際にも、空のディレクトリに関してはカウントしないようにすれば可能
# TODO: もしこちらのファイルを用いてディレクトリを空にする必要がある場合には実行
def main():
    # categories = ["us_politician", "director", "athlete", "dog", "bird", "bread", "car", "aircraft"]
    categories = ["athlete"]
    is_debug = True
    for category in categories:
        logger.info(f"category: {category}")
        data_dir = f"../../../data/clean"  # For cleaned data
        # data_dir = f"../../../data/origin" # For original data
        category_dir = f"{data_dir}/{category}_debug" if is_debug else f"{data_dir}/{category}"
        wikidata_id_dirs = glob.glob(f"{category_dir}/imgs/*/")
        cnt = 0
        for wikidata_id_dir in wikidata_id_dirs:
            if len(glob.glob(f"{wikidata_id_dir}*.jpg")) == 0:
                shutil.rmtree(wikidata_id_dir)
                cnt += 1
        logger.info(f"Remove {cnt} dirs")
        print()


if __name__ == "__main__":
    main()
