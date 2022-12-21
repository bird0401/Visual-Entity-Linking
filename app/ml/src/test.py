import os, traceback, pickle
# import os, gc, math, copy, time, random, joblib, yaml, traceback
# For data manipulation
import numpy as np
# import pandas as pd
# import cv2
# Pytorch Imports
import torch
# import torch.nn as nn
# import torch.optim as optim
# # Utils
# from tqdm import tqdm
# from collections import defaultdict
# from pathlib import Path

from omegaconf import OmegaConf
from PIL import Image, ImageOps

import pickle
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

import sys
import os
# sys.path.append(os.path.join("../../ml/src" , 'entity_linking'))
# from util import *
sys.path.append(os.path.join("../../ml/src" , 'entity_linking/yolov5'))
from utils.plots import Annotator

def annotate_save(img_path, crops_info, wikidata_id, file_name, label = "0", labels = True, save_dir = "/content/save_dir"):
  boxes = crops_info[wikidata_id][file_name]
  print(wikidata_id)
  print(file_name)
  print(boxes)
  if boxes: 
    im = np.array(Image.open(img_path))
    annotator = Annotator(im, example="dog")
    for box in boxes:
      annotator.box_label(box, label if labels else '', color = (0, 255, 0))
    im = annotator.im
    pil_img = Image.fromarray(im)
    print("for saving")
    os.makedirs(f'{save_dir}/{wikidata_id}', exist_ok=True)
    pil_img.save(f'{save_dir}/{wikidata_id}/{file_name}')


img_dir = "../data/detect"
with open(f"{img_dir}/crops_info.pickle", 'rb') as f:
  crops_info = pickle.load(f)

wikidata_id = "Q37600"
file_name = "image_0006.jpg"
file_path = f"runs/detect/{wikidata_id}/{file_name}"
annotate_save(file_path, crops_info, wikidata_id, file_name, save_dir="save_dir_test")
# annotated = annotate_save(file_path, crops_info, wikidata_id, file_name, save_dir="save_dir_test")
