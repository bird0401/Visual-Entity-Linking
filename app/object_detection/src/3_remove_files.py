import glob, os, re, shutil

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def remove_crop_dirs(r_id_dirs):
    # Remove crop directories
    paths = glob.glob(f"{r_id_dirs}/crops")
    for path in paths:
        logger.info(f"remove: {path}")
        shutil.rmtree(path)

def remove_zero_muiti_detect_imgs(r_id_dirs):
    logger.info("Remove multi-detect images")
    paths = glob.glob(f"{r_id_dirs}/crops/*/*.jpg")
    logger.info(f"len(paths): {len(paths)}")
    for path in paths:
        filename = os.path.basename(path)
        if not re.match(r'image_[0-9][0-9][0-9][0-9].jpg', filename):
            path_split = path.split("/")
            path_split[-1] = filename[:10] + filename[-4:]
            another_path = "/".join(path_split)
            logger.info(f"remove: {path}")
            logger.info(f"remove: {another_path}")
            # os.remove(path)
            # os.remove(another_path)
   
    logger.info("Remove original images")
    paths = glob.glob(f"{r_id_dirs}/*.jpg")
    for path in paths:
        logger.info(f"remove: {path}")
        # os.remove(path)

    logger.info("Move from crops to imgs directory")
    paths = glob.glob(f"{r_id_dirs}/crops/*/*.jpg")
    for path in paths:
        dst = "/".join(path.split("/")[:-3])
        logger.info(f"{path} => {dst}")
        # shutil.move(path, dst)
    
    remove_crop_dirs(r_id_dirs)

# TODO: Update
def remove_zero_detect_imgs(r_id_dirs):
    paths = glob.glob(r_id_dirs)
    for path in paths:
        paths_crop = glob.glob(f"{path}/crops/*/*.jpg")
        paths_origin = glob.glob(f"{path}*.jpg")

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

        # remove_crop_dirs(r_id_dirs)

# Change
# - categories
# - is_debug

# CAUTION: MUST NOT EXECUTE TWICE IN THE SAME CATEGORY TO AVOID DELETING ALL IMAGES
def main():
    # categories = ["athlete", "director", "dog", "us_politician"]
    categories = ["athlete"]
    is_debug = True
    for category in categories:
        r_id_dirs = f"../../../data/clean/{category}_debug/imgs/Q*" if is_debug else f"../../../data/clean/data_clean/{category}/imgs/Q*"
        logger.info(f"r_id_dirs: {r_id_dirs}")
        remove_zero_muiti_detect_imgs(r_id_dirs)

    # categories = ["aircraft", "bird", "bread", "car"]
    # for category in categories:
    #     r_id_dirs = f"../../ml/data/{category}_debug/imgs/Q*" if is_debug else f"../../ml/data/{category}/imgs/Q*"
    #     remove_zero_detect_imgs(r_id_dirs)

if __name__=="__main__":
    main()