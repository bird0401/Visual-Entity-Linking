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

model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
model.classes = [16] # predict only dog
model.conf = 0.2
model.to(device)

img_dir = "../data/imgs"
ids = glob.glob(img_dir + '/*')
print(f"num ids: {len(ids)}")

for id in ids:
    paths = glob.glob(f"{id}/*")
    print(f"num paths: {len(paths)}") 
    results = model(paths, size=128)
    results.print()
    save_dir = f'runs/detect/{os.path.basename(id)}'
    results.crop(save_dir=save_dir, exist_ok=True)
    crops = fetch_crops(results)
    with open(f"{save_dir}/crops_info.pickle", mode='wb') as f:
        pickle.dump(crops, f)
    print()