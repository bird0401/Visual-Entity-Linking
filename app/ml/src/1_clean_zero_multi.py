import glob, os, re, shutil

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

# CAUTION: MUST NOT EXECUTE TWICE IN THE SAME CATEGORY
def main():
    # categories = ["athlete", "director", "dog"]
    # categories = ["athlete"]
    # categories = ["us_politician"]
    for category in categories:

        # Remove multi-detect images
        paths = glob.glob(f"../detect_{category}/detect/Q*/crops/*/*.jpg")
        for path in paths:
            filename = os.path.basename(path)
            if not re.match(r'image_[0-9][0-9][0-9][0-9].jpg', filename):
                logger.info(f"remove: {path}")
                os.remove(path)
                path_split = path.split("/")
                path_split[-1] = filename[:10] + filename[-4:]
                another_path = "/".join(path_split)
                if os.path.isfile(another_path):
                    logger.info(f"another remove: {another_path}")
                    os.remove(another_path)

        # Remove original images
        paths = glob.glob(f"../detect_{category}/detect/Q*/*.jpg")
        for path in paths:
            logger.info(f"remove: {path}")
            os.remove(path)

        # Move to original directory
        paths = glob.glob(f"../detect_{category}/detect/Q*/crops/*/*.jpg")
        for path in paths:
            dst = "/".join(path.split("/")[:-3])
            logger.info(f"{path} => {dst}")
            shutil.move(path, dst)

if __name__=="__main__":
    main()