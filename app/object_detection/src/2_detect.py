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

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
set_seed(2022)
is_debug = False

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

data_dir = "../../../data"

model = torch.hub.load("ultralytics/yolov5", "yolov5l", pretrained=True)
model.conf = 0.4
model.max_det = 2


def detect_images_by_id(ids_dir_path, clean_dir):
    try:
        logger.info(f"ids_dir_path: {ids_dir_path}")
        
        id = ids_dir_path.split('/')[-1]
        save_dir = f"{clean_dir}/{id}"
        if os.path.exists(save_dir):
            logger.info(f"save_dir {save_dir} already exists")
            return
        logger.info(f"save_dir: {save_dir}")
        
        image_paths = glob.glob(f"{ids_dir_path}/*")
        logger.info(f"num image_paths: {len(image_paths)}")

        results = model(image_paths, size=128)
        results.print()
        results.crop(save_dir=save_dir, exist_ok=True)

        # wikidata_id = ids_path.split("/")[-1]
        # logger.debug(f"wikidata_id : {wikidata_id}")
        # crops[wikidata_id] = fetch_crops(results)

    except Exception:
        logger.info(f"ids_dir_path: {ids_dir_path}")
        traceback.print_exc()

# カテゴリごとに物体認識を行う
def detect(category):
    logger.info(f"category: {category}")

    img_dir = f"{data_dir}/{category}_debug/images" if is_debug else f"{data_dir}/{category}/images"
    clean_dir = f"{img_dir}/clean" 

    # TODO: create module to define it
    # change model.size

    model.classes = map_category_to_num[category]  # Category to predict
    model.to(device)

    ids_dir_paths = glob.glob(f"{img_dir}/origin/*")
    logger.info(f"num ids in {category} directory: {len(ids_dir_paths)}")

    # TODO: 危険なので一旦コメントアウト。
    # print(f"clean_dir: {clean_dir}")
    # shutil.rmtree(clean_dir, ignore_errors=True)
    # crops = {}

    # それぞれのidごとの画像が物体検出器に渡される
    # cropした結果がcleanに保存される
    for ids_dir_path in ids_dir_paths:
        detect_images_by_id(ids_dir_path, clean_dir)

    # wikidata_id = ids_paths[0].split("/")[-1]
    # logger.debug(f'wikidata_id : {wikidata_id}')
    # logger.debug(f'crops[wikidata_id] : {crops[wikidata_id]}')

    # with open(f"{save_dir}/crops_info.pickle", mode='wb') as f:
    #     pickle.dump(crops, f)
        
    logger.info(f"finish detect {category}")
                
# 注意: 対象ディレクトリを削除してから実行すること
def main():
    # categories = [
    #     "aircraft",
    #     "athlete",
    #     "bread",
    #     "bird",
    #     "car",
    #     "director",
    #     "dog",
    #     "us_politician",
    # ]

    category = sys.argv[1]
    detect(category)


if __name__ == "__main__":
    main()
