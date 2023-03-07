from collections import Counter, defaultdict
import glob

import matplotlib.pyplot as plt

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')


def main():
    categories = ["us_politician", "director", "athlete", "dog", "bird", "bread", "car", "aircraft"]
    sum_entites, sum_images = 0, 0
    num_imgs = defaultdict(int)
    for category in categories:
        logger.info(f"category: {category}")
        wikidata_id_dirs = glob.glob(f"../detect_{category}/detect/*/") # for cleaned data
        # wikidata_id_dirs = glob.glob(f"../../object_detection/data_{category}/imgs/*/") # for original data
        logger.info(f"num entites: {len(wikidata_id_dirs)}")
        sum_entites += len(wikidata_id_dirs)
        for wikidata_id_dir in wikidata_id_dirs:
            wikidata_id = wikidata_id_dir.split("/")[-2]
            filenames = glob.glob(f"{wikidata_id_dir}*.jpg")
            num_imgs[wikidata_id] = len(filenames)
        # logger.info(f"sum of images: {sum_imgs_per_category}")
        # logger.info(f"images per entity: {(sum_imgs_per_category / len(wikidata_id_dirs)):.3g}")
        # print()
    counter = Counter(num_imgs.values())
    sum_imgs_per_category = sum([num*n for num, n in counter.items()])
    sum_images += sum_imgs_per_category
    plt.xscale("log")
    plt.yscale("log")
    print(counter)
    plt.scatter(counter.keys(), counter.values(), s=1, c="#1f77b4")
    plt.grid(True)
    plt.savefig(f"../images/scatter2.pdf", bbox_inches="tight", pad_inches=0.05)
        # plt.savefig(f"../figures/scatter_{category}.pdf", bbox_inches="tight", pad_inches=0.05)
    logger.info(f"sum entites: {sum_entites}, sum images: {sum_images}, images per all entity: {(sum_images / sum_entites):.3g}")

if __name__=="__main__":
    main()
