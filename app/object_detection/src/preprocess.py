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


if __name__=="__main__":
    img_dir = "../data/imgs"
    # img_dir = "../data_debug/imgs"
    paths = glob.glob(f"{img_dir}/*/*")
    logger.info(f"num images: {len(paths)}")

    start_time = time.time()

    with Pool() as p:
        imap = p.imap(delete_exif, paths)
        results = list(tqdm(imap, total=len(paths)))

    logger.info("done")
    logger.info(f"elapsed time: {time.time() - start_time}")

