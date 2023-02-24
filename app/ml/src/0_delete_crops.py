import glob, shutil

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    categories = ["aircraft", "bird", "bread", "car"]
    for category in categories:
        paths = glob.glob(f"../detect_{category}/detect/Q*/crops/")
        for path in paths:
            logger.info(path)
            shutil.rmtree(path)

if __name__=="__main__":
    main()