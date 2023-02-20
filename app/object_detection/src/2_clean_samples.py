import os, glob, pickle
from yolo_detection.util import *
import torch

from PIL import Image                                                                                         
Image.MAX_IMAGE_PIXELS = None # Enable to read large size images

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

# Change demands on the situation
# - category
# - debug

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
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    set_seed(2022) 

    category = "aircraft"

    map_category_to_num = {
        "aircraft": [4],
        "athlete": [0],
        "bird": [14],
        "bread": [45, 48, 52, 53, 54, 55],
        "car": [2],
        "director": [0],
        "dog": [16],
        "us_politician": [0]
    }

    # TODO: create module to define it
    model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
    model.classes = map_category_to_num[category] # Category to predict
    model.conf = 0.2 # change
    model.to(device)

    img_dir = f"../sample_{category}" 
    paths = glob.glob(f"{img_dir}/*")
    logger.info(f"num paths: {len(paths)}")

    save_dir = f"../clean_samples/{category}"
    logger.info(f"save_dir: {save_dir}")

    try:
        results = model(paths, size=640) # change size
        results.print()
        results.save(save_dir=save_dir, exist_ok=True)
    except Exception: 
        logger.info(f"ids_path: {ids_path}")
        traceback.print_exc()

if __name__=="__main__":
    main()
