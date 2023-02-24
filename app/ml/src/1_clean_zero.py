import glob, os, re

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    paths_id = glob.glob("../detect_car/detect/Q*/")
    for path_id in paths_id:
        paths_crop = glob.glob(f"{path_id}crops/*/*.jpg")
        paths_origin = glob.glob(f"{path_id}*.jpg")

        crop_filenames = []
        # for i, path_crop in enumerate(paths_crop):
        for path_crop in paths_crop:
            filename = os.path.basename(path_crop)
            # if not re.match(r'image_[0-9][0-9][0-9][0-9].jpg', filename):
            #     filename = filename[:10] + filename[-4:]
            crop_filenames.append(filename)

        for path_origin in paths_origin:
            origin_filename = os.path.basename(path_origin)
            if origin_filename not in crop_filenames:
                logger.info(f"remove: {path_origin}")
                os.remove(path_origin)

if __name__=="__main__":
    main()