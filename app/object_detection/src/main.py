import os, glob, pickle
from yolo_detection.util import *
import torch

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
set_seed(2022) 

# TODO: create module to define it
model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
model.classes = [16] # predict only dog
model.conf = 0.2 
model.to(device)

img_dir = "../data/imgs"
ids_paths = glob.glob(img_dir + '/*')
logger.info(f"num ids: {len(ids_paths)}")

crops = {}
for ids_path in ids_paths:
    paths = glob.glob(f"{ids_path}/*")
    logger.info(f"num paths: {len(paths)}") 
    results = model(paths, size=128)
    results.print()
    save_dir = f'runs/detect/{os.path.basename(ids_path)}'
    results.crop(save_dir=save_dir, exist_ok=True)
    wikidata_id = ids_path.split("/")[-1]
    logger.debug(f"wikidata_id : {wikidata_id}")
    crops[wikidata_id] = fetch_crops(results)
    print()

wikidata_id = ids_paths[0].split("/")[-1]
logger.debug(f'wikidata_id : {wikidata_id}')
logger.debug(f'crops[wikidata_id] : {crops[wikidata_id]}')
with open(f"runs/detect/crops_info.pickle", mode='wb') as f:
    pickle.dump(crops, f)