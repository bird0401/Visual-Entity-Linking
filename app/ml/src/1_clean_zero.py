import glob, os, shutil

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
        paths_id = glob.glob(f"../detect_{category}/detect/Q*/")
        for path_id in paths_id:
            paths_crop = glob.glob(f"{path_id}crops/*/*.jpg")
            paths_origin = glob.glob(f"{path_id}*.jpg")

            # Remove no detect files
            crop_filenames = []
            for path_crop in paths_crop:
                filename = os.path.basename(path_crop)
                crop_filenames.append(filename)
            for path_origin in paths_origin:
                origin_filename = os.path.basename(path_origin)
                if origin_filename not in crop_filenames:
                    logger.info(f"remove: {path_origin}")
                    # os.remove(path_origin)

            # Remove crop dirs
            paths = glob.glob(f"../detect_{category}/detect/Q*/crops/")
            for path in paths:
                logger.info(path)
                # shutil.rmtree(path)

if __name__=="__main__":
    main()