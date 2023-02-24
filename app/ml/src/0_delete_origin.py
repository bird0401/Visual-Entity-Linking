import glob, os

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    categories = ["athlete", "director", "dog"]
    # categories = ["athlete", "director", "dog", "us_politician"]
    for category in categories:
        # paths = glob.glob(f"../detect_{category}/detect/Q*/crops/")
        paths = glob.glob(f"../detect_{category}/detect/Q*/*.jpg")
        for path in paths:
            logger.info(path)
            os.remove(path)

if __name__=="__main__":
    main()