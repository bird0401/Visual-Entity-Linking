import glob, shutil

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    # categories = ["us_politician", "director", "athlete", "dog", "bird", "bread", "car", "aircraft"]
    categories = ["athlete"]
    is_debug = True
    for category in categories:
        logger.info(f"category: {category}")
        data_dir = f"../../../data/clean" # For cleaned data
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

if __name__=="__main__":
    main()