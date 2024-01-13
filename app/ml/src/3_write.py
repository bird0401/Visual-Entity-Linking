import glob, json, sys

from tqdm import tqdm
# import numpy as np
# import h5py
# import cv2
import logging

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

map_id_to_label = {}

# data_dir = "../../../data/origin"
data_dir = "../../../data"

# TODO: 現状map_id_to_labelを作成する機能以外はコメントアウトした状態なので、もう一度h5を作成するときはそれらを戻してから実行すること
def fetch_label(id_wikidata):
    assert type(id_wikidata) == str
    if id_wikidata not in map_id_to_label:
        map_id_to_label[id_wikidata] = len(map_id_to_label)
    return map_id_to_label[id_wikidata]


def fetch_variables(path, img_size=512):
    # img = cv2.imread(path)
    # img = cv2.resize(img, (img_size, img_size))
    id_wikidata = path.split("/")[-2]
    label = fetch_label(id_wikidata)
    # return img, id_wikidata, label


def process_batch(f, paths, start_idx, end_idx, img_size=512):
        imgs = []
        id_wikidatas = []
        labels = []
        for j in range(start_idx, end_idx):
            path = paths[j]

            # TODO: for only generating map_id_to_label
            fetch_variables(path, img_size)
            # img, id_wikidata, label = fetch_variables(path, img_size)

        #     imgs.append(img)
        #     id_wikidatas.append(id_wikidata)
        #     labels.append(label)
        # f["path"][start_idx:end_idx] = paths[start_idx:end_idx]
        # f["img"][start_idx:end_idx] = np.array(imgs)
        # f["id_wikidata"][start_idx:end_idx] = id_wikidatas
        # f["label"][start_idx:end_idx] = labels


def create_dataset(paths, save_file_name):
    num_data = len(paths)
    batch_size = 128
    num_batches = num_data // batch_size
    img_size = 224
    # str_dtype = h5py.special_dtype(vlen=str)
    
    # with h5py.File(save_file_name, "w") as f:
    with open(save_file_name, "w") as f:
        # f.create_dataset("path", shape=(num_data, ), dtype=str_dtype)
        # f.create_dataset("img", shape=(num_data, img_size, img_size, 3))
        # f.create_dataset("id_wikidata", shape=(num_data, ), dtype=str_dtype)
        # f.create_dataset("label", shape=(num_data, ), dtype=np.int32)

        for i in tqdm(range(num_batches)):
            start_idx = i * batch_size
            end_idx = (i+1) * batch_size
            process_batch(f, paths, start_idx, end_idx, img_size)

        if num_data % batch_size != 0:
            start_idx = num_batches * batch_size
            end_idx = num_data
            process_batch(f, paths, start_idx, end_idx, img_size)

        # f.create_dataset("out_features", data=len(map_id_to_label), shape=(1,), dtype=np.int32)

    logger.info(f"num of images: {len(paths)}")
    logger.info(f"out_features: {len(map_id_to_label)}")

    print()

# wisteriaのファイル数制限に対応するため、h5ファイルを作成
def create_file(category):
    category_dir = f"{data_dir}/{category}"
    assert type(category_dir) == str
    logger.info(f"category_dir: {category_dir}")
    # map_id_to_label = {}

    # for mode in ["train", "val", "test"]:
    for mode in ["train", "test"]:
        logger.info(f"mode: {mode}")

        # TODO: for only generating map_id_to_label
        save_file_name = f"{category_dir}/for_map_id_to_label_{mode}.h5"
        # save_file_name = f"{category_dir}/{mode}.h5"

        logger.info(f"save_file_name: {save_file_name}")

        # TODO: 危険なのでコメントアウト。手動でdeleteすること
        # if os.path.exists(filename):
        #     os.remove(filename)
        # os.makedirs(os.path.dirname(filename), exist_ok=True)

        paths = glob.glob(f"{category_dir}/{mode}/Q*/*.jpg")
        create_dataset(paths, save_file_name)
    
    with open(f"{category_dir}/map_id_to_label.json", 'w') as f:
        json.dump(map_id_to_label, f, indent=2)


# Change
# img_size
# TODO: 今後originに対してMLを行う場合、originディレクトリ内にh5ファイルを作成するようにする
# 20000エンティティ(director, us_politician)で約1.5時間かかる
def main():
    categories = ["athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = ["aircraft"]
    for category in categories:
    # category = sys.argv[1]
        create_file(category)


if __name__ == "__main__":
    main()




