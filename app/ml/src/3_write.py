import os, glob, traceback
from tqdm import tqdm
import numpy as np
import h5py
import cv2
import logging

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def insert_data(f, path, label, id_wikidata, cnt):
    assert f is not None
    assert type(path) == str
    assert type(label) == int
    assert type(id_wikidata) == str
    assert type(cnt) == int
    try:
        img = cv2.imread(path)
        img = img[np.newaxis, :, :, :]
        str_dtype = h5py.special_dtype(vlen=str)
        f["path"].create_dataset(str(cnt), data=path, shape=(1,), dtype=str_dtype)
        f["img"].create_dataset(str(cnt), data=img)
        f["label"].create_dataset(str(cnt), data=label, shape=(1,), dtype=np.int32)
        f["id_wikidata"].create_dataset(str(cnt), data=id_wikidata, shape=(1,), dtype=str_dtype)
    except Exception:
        traceback.print_exc()
    return f


def fetch_label(id_wikidata, map_id_to_label):
    assert type(id_wikidata) == str
    if id_wikidata not in map_id_to_label:
        map_id_to_label[id_wikidata] = len(map_id_to_label)
    return map_id_to_label[id_wikidata]


def create_groups(f):
    assert f
    f.create_group("path")
    f.create_group("img")
    f.create_group("label")
    f.create_group("id_wikidata")
    return None


def create_dataset(category_dir):
    assert type(category_dir) == str
    logger.info(f"category_dir: {category_dir}")
    map_id_to_label = {}

    for mode in ["train", "val", "test"]:
        logger.info(f"mode: {mode}")

        filename = f"{category_dir}/{mode}.h5"
        logger.info(f"filename: {filename}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with h5py.File(filename, "w") as f:
            create_groups(f)
            cnt = 0
            entity_dirs = glob.glob(f"{category_dir}/{mode}/Q*")

            for entity_dir in tqdm(entity_dirs):
                paths = glob.glob(f"{entity_dir}/*.jpg")
                id_wikidata = entity_dir.split("/")[-1]
                label = fetch_label(id_wikidata, map_id_to_label)
                # print(id_wikidata, label)

                for path in paths:
                    f = insert_data(f, path, label, id_wikidata, cnt)
                    cnt += 1

            logger.info(f"num of images: {cnt}")
            logger.info(f"out_features: {len(map_id_to_label)}")
            f.create_dataset("out_features", data=len(map_id_to_label), shape=(1,), dtype=np.int32)
            print()

def main():
    data_dir = "../../../data/clean"
    dir_names = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # dir_names = ["athlete"]
    # dir_names = ["us_politician"]
    for dir_name in dir_names:
        category_dir = f"{data_dir}/{dir_name}"
        create_dataset(category_dir)


if __name__ == "__main__":
    main()
