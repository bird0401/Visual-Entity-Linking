import os, glob
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
set_seed(2022) # TODO 

model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
model.classes = [16] # predict only dog
model.conf = 0.2
model.to(device)

img_dir = "../data/imgs"
ids = glob.glob(img_dir + '/*')
logger.info(f"num ids: {len(ids)}")

for id in ids:
    paths = glob.glob(f"{id}/*")
    logger.info(f"num paths: {len(paths)}") 
    results = model(paths, size=128)
    results.print()
    results.save(save_dir=f'runs/detect/{os.path.basename(id)}') 
    print()
    
    # index of names and paths should be linked
    # names = results.pandas().xyxy
    # for i in range(len(names)):
    #     if "dog" not in list(names[i].name): 
    #         print(i, paths[i]) 