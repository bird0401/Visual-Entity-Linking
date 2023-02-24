from collections import Counter, defaultdict
import glob, os

import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')


def main():
    category_dirs = glob.glob("../detect_*/")
    sum_entites, sum_images = 0, 0
    for category_dir in category_dirs:
        category = category_dir.split("/")[-2][7:]
        logger.info(f"category: {category}")
        wikidata_id_dirs = glob.glob(f"{category_dir}detect/*/")
        logger.info(f"num entites: {len(wikidata_id_dirs)}")
        sum_entites += len(wikidata_id_dirs)
        num_imgs = defaultdict(int)
        for wikidata_id_dir in wikidata_id_dirs:
            wikidata_id = wikidata_id_dir.split("/")[-2]
            filenames = glob.glob(f"{wikidata_id_dir}*.jpg")
            num_imgs[wikidata_id] = len(filenames)
            # for filename in filenames:
                # num_imgs[wikidata_id] = sum(os.path.isfile(os.path.join(target_dir, name)) for name in os.listdir(target_dir))
        # print(num_imgs.values())
        counter = Counter(num_imgs.values())
        sum_imgs_per_category = sum([num*n for num, n in counter.items()])
        sum_images += sum_imgs_per_category
        logger.info(f"sum of images: {sum_imgs_per_category}")
        logger.info(f"images per entity: {(sum_imgs_per_category / len(wikidata_id_dirs)):.3g}")
        print()
        plt.scatter(counter.keys(), counter.values(), s=1, c="#1f77b4")
        # matplotlib.pyplot.scatter(x, y, s=20, c=None, marker='o', cmap=None, norm=None,
        #                         vmin=None, vmax=None, alpha=None, linewidths=None,
        #                         verts=None, edgecolors=None, hold=None, data=None,
        #                         **kwargs)
        plt.grid(True)
        # plt.rcParams['font.family'] = 'IPAexGothic'
        # plt.rcParams['xtick.labelsize'] = 9 # 軸だけ変更されます。
        # plt.rcParams['ytick.labelsize'] = 24 # 軸だけ変更されます
        # plt.rcParams['axes.linewidth'] = 1.0 # axis line width
        plt.savefig(f"../scatter_{category}.png", bbox_inches="tight", pad_inches=0.05)
    logger.info(f"sum entites: {sum_entites}, sum images: {sum_images}, images per all entity: {(sum_images / sum_entites):.3g}")

if __name__=="__main__":
    main()
