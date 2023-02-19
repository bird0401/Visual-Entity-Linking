import glob, random, shutil, os

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def main():
    path_ids = glob.glob("../data_bird/imgs/*") # change directory name by category
    path_ids_sample = random.sample(path_ids, 10)
    dst_dir = "../data_bird_debug/imgs"
    try:
        os.makedirs(dst_dir, exist_ok=True)
    except FileExistsError:
        logger.info("exists")
    for src_dir in path_ids_sample:
        logger.info(src_dir)
        id_sample = src_dir.split("/")[-1]
        shutil.copytree(src_dir, f"{dst_dir}/{id_sample}")

if __name__ == '__main__':
  main()
