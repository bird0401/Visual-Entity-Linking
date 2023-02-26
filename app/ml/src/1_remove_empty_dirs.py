import glob, shutil

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    categories = ["us_politician", "director", "athlete", "dog", "bird", "bread", "car", "aircraft"]
    for category in categories:
        logger.info(f"category: {category}")
        # wikidata_id_dirs = glob.glob(f"../detect_{category}/detect/*/") # for cleaned data
        wikidata_id_dirs = glob.glob(f"../../object_detection/data_{category}/imgs/*/") # for original data
        cnt = 0
        for wikidata_id_dir in wikidata_id_dirs:
            if len(glob.glob(f"{wikidata_id_dir}*.jpg")) == 0:
                shutil.rmtree(wikidata_id_dir)
                cnt += 1
        logger.info(f"Remove {cnt} dirs")
        print()

if __name__=="__main__":
    main()