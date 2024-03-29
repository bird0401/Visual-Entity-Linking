import glob, joblib, os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def GetWikidataId(path):
    return path.split("/")[-2]


# def GetNonCropPath(path):
#   path_split = path.split("/")
#   basename_split = path_split[-1].split(".")
#   basename = basename_split[0][:10] + "." + basename_split[1]
#   parents_split = path_split[:-3]
#   path_noncrop = ""
#   for s in parents_split:
#     path_noncrop += (s + "/")
#   path_noncrop += basename
#   return path_noncrop


def Encoding(df, save_file):
    encoder = LabelEncoder()
    df["label"] = encoder.fit_transform(df["wikidata_id"])
    with open(f"{save_file}.pkl", "wb") as fp:
        joblib.dump(encoder, fp)
    return df


# Extract images with more than or equal to 5 images
def DeleteSmallLabels(df):
    vc = df["wikidata_id"].value_counts()
    used_wikidata_id = vc[vc >= 5].index
    df = df[df["wikidata_id"].isin(used_wikidata_id)]
    df = df.reset_index(drop=True)
    return df


# def Split_Kfold(df, n_fold):
#   train_val_indices, test_indices = train_test_split(list(range(len(df.label))), test_size=0.2, stratify=df.label)
#   df.loc[train_val_indices, "is_train_val"] = 1
#   df.loc[test_indices, "is_train_val"] = 0
#   df_train, df_test = df[df["is_train_val"] == 1].reset_index(drop = True), df[df["is_train_val"] == 0].reset_index(drop = True)
#   logger.debug(f'len(df_train): {len(df_train)}, len(df_test): {len(df_test)}')

#   skf = StratifiedKFold(n_splits=n_fold)
#   for fold, ( _, val_) in enumerate(skf.split(X=df_train, y=df_train.label)):
#         df_train.loc[val_ , "kfold"] = fold
#   return df_train, df_test

# TODO: val, testの両方を生成しているが、同じ元データからこれらの分割を行ってもあまり意味がない。仮にtestをするならば、今回の収集元とは違うデータを用意するべき。
# TODO: kfoldが必要か確認
def split_train_val_test(df):
    train_val_indices, test_indices = train_test_split(list(range(len(df.label))), test_size=0.2, stratify=df.label)
    df.loc[train_val_indices, "is_train_val"] = 1
    df.loc[test_indices, "is_train_val"] = 0
    df_train, df_test = (
        df[df["is_train_val"] == 1].reset_index(drop=True),
        df[df["is_train_val"] == 0].reset_index(drop=True),
    )
    logger.debug(f"len(df_train): {len(df_train)}, len(df_test): {len(df_test)}")

    # train_indices, val_indices = train_test_split(list(range(len(df_train.label))), test_size=0.25, stratify=df_train.label)
    # logger.info(f"len(train_indices): {len(train_indices)}, len(val_indices): {len(val_indices)}")
    # df_train.loc[train_indices, "kfold"] = 1
    # df_train.loc[val_indices, "kfold"] = 0
    return df_train, df_test


# TODO: aircraftのみを用いてMLの最後までできるかを確かめる。時間がかかりそうな処理があったらそれは他のカテゴリでも実行しておく
# TODO: 必要であればoriginのcsvを作成し、cleanと同様に実験を行う
# Change demands on the situation
# - categories
# - is_debug
# - data_dir
def main():
    # categories = ["athlete"]
    categories = [
        # "aircraft",
        "athlete",
        "bread",
        "bird",
        "car",
        "director",
        "dog",
        "us_politician",
    ]
    # categories = ["aircraft"]
    is_debug = False
    logger.info(f"debug mode") if is_debug else logger.info(f"production mode")

    for category in categories:
        logger.info(f"category: {category}")

        data_dir = f"../../../data"
        category_dir = f"{data_dir}/{category}_debug" if is_debug else f"{data_dir}/{category}"
        image_paths = glob.glob(f"{category_dir}/images/clean/*/*.jpg")

        df = pd.DataFrame(image_paths, columns=["path"])
        logger.debug(f"df['path'][0] : {df['path'][0]}")
        # df['path_noncrop'] = df['path'].apply(GetNonCropPath)
        # logger.debug(f"df['path_noncrop'][0] : {df['path_noncrop'][0]}")
        df["wikidata_id"] = df["path"].apply(lambda x: x.split("/")[-2])
        logger.debug(f"df['wikidata_id'][0] : {df['wikidata_id'][0]}")
        df["file_name"] = df["path"].apply(lambda x: x.split("/")[-1])
        logger.debug(f"df['file_name'][0] : {df['file_name'][0]}")

        # df = df.sample(frac=0.3) # execute if creating sample dataframe

        df = DeleteSmallLabels(df)
        df = Encoding(df, "crop")
        logger.info(f"len(df['label'].unique()) = {len(df['label'].unique())}")
        logger.info(f"len(df) = {len(df)}")
        os.makedirs(f"{category_dir}/csv", exist_ok=True)
        df.to_csv(f"{category_dir}/csv/origin.csv", index=False)

        # csv for train and test
        df_train, df_test = split_train_val_test(df)
        # df_train, df_test = Split_Kfold(df, 3)
        logger.info(f"len(df_train) = {len(df_train)}")
        logger.info(f"len(df_test) = {len(df_test)}")
        df_train.to_csv(f"{category_dir}/csv/train.csv", index=False)
        df_test.to_csv(f"{category_dir}/csv/test.csv", index=False)
        print()


if __name__ == "__main__":
    main()
