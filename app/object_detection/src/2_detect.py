import sys, os, glob, pickle, shutil
from yolo_detection.util import *
import torch

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Enable to read large size images

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# Change demands on the situation
# - category
# - debug

def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    set_seed(2022)

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
    is_debug = True

    map_category_to_num = {
        "aircraft": [4],
        "athlete": [0],
        "bird": [14],
        "bread": [48, 52, 53, 54, 55],
        "car": [2],
        "director": [0],
        "dog": [16],
        "us_politician": [0],
    }

    for category in categories:
        logger.info(f"category: {category}")

        # TODO: create module to define it
        # change model.size
        model = torch.hub.load("ultralytics/yolov5", "yolov5l", pretrained=True)
        model.classes = map_category_to_num[category]  # Category to predict
        model.conf = 0.4
        model.max_det = 2
        model.to(device)

        img_dir = f"../../../data/origin/{category}_debug/imgs" if is_debug else f"../../../data/origin/{category}/imgs"
        ids_paths = glob.glob(img_dir + "/*")
        logger.info(f"num ids: {len(ids_paths)}")

        save_dir = f"../../../data/clean/{category}_debug/imgs" if is_debug else f"../../data/clean/{category}/imgs"
        shutil.rmtree(save_dir, ignore_errors=True)
        # crops = {}

        for ids_path in ids_paths:
            try:
                paths = glob.glob(f"{ids_path}/*")
                logger.info(f"num paths: {len(paths)}")
                results = model(paths, size=128)
                # print(inspect.getsource(results.print()))
                results.print()
                results.crop(save_dir=f"{save_dir}/{os.path.basename(ids_path)}", exist_ok=True)
                # wikidata_id = ids_path.split("/")[-1]
                # logger.debug(f"wikidata_id : {wikidata_id}")
                # crops[wikidata_id] = fetch_crops(results)
            except Exception:
                logger.info(f"ids_path: {ids_path}")
                traceback.print_exc()

        # wikidata_id = ids_paths[0].split("/")[-1]
        # logger.debug(f'wikidata_id : {wikidata_id}')
        # logger.debug(f'crops[wikidata_id] : {crops[wikidata_id]}')

        # with open(f"{save_dir}/crops_info.pickle", mode='wb') as f:
        #     pickle.dump(crops, f)


if __name__ == "__main__":
    main()
