import time
from tqdm import tqdm
from multiprocessing import Pool
from yolo_detection.util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# Change demands on the situation
# - category
# - is_debug

# TODO: 物体検出できないファイルを削除するためのものだが、単に物体検出の際に例外処理を使えば良いのではないか
# TODO: ここで削除しているファイルは実際に開いても利用できないものばかりであるため、ここで削除しておいて正解かもしれない
def main():
    categories = [
        "aircraft",
        "athlete",
        "bread",
        "bird",
        "car",
        "director",
        "dog",
        "us_politician",
    ]
    is_debug = False
    data_dir = "../../../data"
    for category in categories:
        logger.info(f"category: {category}")
        img_dir = f"{data_dir}/{category}_debug/images" if is_debug else f"{data_dir}/{category}/images"  # for debug
        print(f"img_dir: {img_dir}")
        # img_dir = f"../data/{category}_debug/imgs" if is_debug else f"../data/{category}/imgs"  # for debug
        # paths = glob.glob(f"{img_dir}/origin/*/*")
        paths = glob.glob(f"{img_dir}/origin/*/*")
        assert len(paths) != 0, f"num images: {len(paths)}"
        logger.info(f"img_dir: {img_dir}")
        logger.info(f"num images: {len(paths)}")

        # Mutil-processing
        start_time = time.time()
        with Pool() as p:
            imap = p.imap(delete_exif, paths)
            results = list(tqdm(imap, total=len(paths)))
        logger.info("done")
        logger.info(f"elapsed time: {time.time() - start_time}")


if __name__ == "__main__":
    main()
