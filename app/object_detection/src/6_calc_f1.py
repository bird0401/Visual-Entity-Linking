import glob

import pandas as pd
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def main():
    conf = "0.8"  # change
    logger.info(f"conf: {conf}")
    dir_name = "clean_samples_no_delete"
    caterogy_paths = glob.glob(f"../{dir_name}/clean_samples_{conf}/*/*.*")
    df = pd.DataFrame()
    df["paths"] = caterogy_paths
    df["label"] = df["paths"].str.contains(f"\.\./{dir_name}/clean_samples_{conf}/.*/image_...nm?\.jpg")
    df["pred"] = df["paths"].str.contains(f"\.\./{dir_name}/clean_samples_{conf}/.*/image_...n?m\.jpg")
    df.loc[df["paths"].str.contains(f"\.\./{dir_name}/clean_samples_{conf}/.*/image_....*FN\.jpg"), "label",] = True
    df.loc[df["paths"].str.contains(f"\.\./{dir_name}/clean_samples_{conf}/.*/image_....*FN\.jpg"), "pred",] = False
    logger.info(f'len(df["paths"]): {len(df["paths"])}')
    logger.info(f'num noise: {df["pred"].sum()}')
    logger.info(f'precision_score: {precision_score(df["label"], df["pred"])}')
    logger.info(f'recall_score: {recall_score(df["label"], df["pred"])}')
    logger.info(f'f1_score: {f1_score(df["label"], df["pred"])}')


if __name__ == "__main__":
    main()
