import os, glob, traceback
from tqdm import tqdm
import numpy as np
import h5py
import cv2
import logging

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('data')

# categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
data_dir = "../../../data"
type = "clean"
categories = ["athlete"]
is_debug = True
# mode = "train"
mode = "val"
map_id_to_label = {}

for category in categories:
    logger.info(f"category: {category}")
    category = f"{category}_debug" if is_debug else category
    os.makedirs(f"{data_dir}/{type}/{category}", exist_ok=True)
    filename = f"{data_dir}/{type}/{category}/{mode}.h5"
    logger.info(f"filename: {filename}")
    with h5py.File(filename,'w') as f:
        out_features = f.create_dataset("out_features", data=len(map_id_to_label), shape=(1,), dtype=np.int8)
        img_data = f.create_group("img")
        label_data = f.create_group("label")
        id_data = f.create_group("id_wikidata")
        path_data = f.create_group("path")
        cnt = 0 
        entity_dirs = glob.glob(f"../../../data/clean/athlete_debug/imgs/Q*")
        for entity_dir in tqdm(entity_dirs):
            paths = glob.glob(f"{entity_dir}/*.jpg")
            id_wikidata = entity_dir.split("/")[-1]
            if id_wikidata not in map_id_to_label.keys():
                map_id_to_label[id_wikidata] = len(map_id_to_label)
            label = map_id_to_label[id_wikidata]
            for path in paths:
                try:
                    img = cv2.imread(path)
                    str_dtype = h5py.special_dtype(vlen=str)
                    img_data.create_dataset(str(cnt), data=img)
                    label_data.create_dataset(str(cnt), data=label, shape=(1,), dtype=np.int8)
                    id_data.create_dataset(str(cnt), data=id_wikidata, shape=(1,), dtype=str_dtype)
                    path_data.create_dataset(str(cnt), data=path, shape=(1,), dtype=str_dtype)
                    cnt += 1
                except Exception:
                    traceback.print_exc()
