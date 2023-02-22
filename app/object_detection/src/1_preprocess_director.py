import time
from tqdm import tqdm
from multiprocessing import Pool
from yolo_detection.util import *

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

# Change demands on the situation
# - category
# - is_debug

# List of categories
# - aircraft
# - athlete
# - bird
# - bread
# - car
# - director
# - dogs
# - us_politician
def main():
    category = "director" 
    is_debug = False
    img_dir = f"../data_{category}_debug/imgs" if is_debug else f"../data_{category}/imgs" # for debug
    paths = glob.glob(f"{img_dir}/*/*")
    logger.info(f"img_dir: {img_dir}")
    logger.info(f"num images: {len(paths)}")

    start_time = time.time()

    # Mutil-processing
    with Pool() as p:
        imap = p.imap(delete_exif, paths)
        results = list(tqdm(imap, total=len(paths)))

    logger.info("done")
    logger.info(f"elapsed time: {time.time() - start_time}")

if __name__=="__main__":
    main()

