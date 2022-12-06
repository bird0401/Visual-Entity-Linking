import glob, joblib, os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

def GetWikidataId(path):
  return path.split("/")[-4]

def Encoding(df, save_file):
  encoder = LabelEncoder()
  df['label'] = encoder.fit_transform(df['wikidata_id'])
  with open(f"{save_file}.pkl", "wb") as fp:
      joblib.dump(encoder, fp)
  return df

# Extract images with more than or equal to 3 images
def DeleteSmallLabels(df):
    vc = df['wikidata_id'].value_counts()
    used_wikidata_id = vc[vc >= 5].index
    df = df[df["wikidata_id"].isin(used_wikidata_id)]
    df = df.reset_index(drop = True)
    return df

def Split_Kfold(df, n_fold):
  train_val_indices, test_indices = train_test_split(list(range(len(df.label))), test_size=0.2, stratify=df.label)
  df.loc[train_val_indices, "is_train_val"] = 1
  df.loc[test_indices, "is_train_val"] = 0
  df_train, df_test = df[df["is_train_val"] == 1].reset_index(drop = True), df[df["is_train_val"] == 0].reset_index(drop = True)
  logger.debug(f'len(df_train): {len(df_train)}, len(df_test): {len(df_test)}')

  skf = StratifiedKFold(n_splits=n_fold)
  for fold, ( _, val_) in enumerate(skf.split(X=df_train, y=df_train.label)):
        df_train.loc[val_ , "kfold"] = fold
  return df_train, df_test


mount_dir = "../data"

# get file paths
l = glob.glob(f'{mount_dir}/detect/**/crops/dog/*')

df = pd.DataFrame(l, columns=["path"])
df['wikidata_id'] = df['path'].apply(GetWikidataId)
df = DeleteSmallLabels(df)
df = Encoding(df, "crop")

logger.info(f'len(df) = {len(df)}')
os.makedirs(f"{mount_dir}/csv", exist_ok=True)
df.to_csv(f"{mount_dir}/csv/origin.csv", index=False)

# csv for train and test 
df_train, df_test = Split_Kfold(df, 5)
logger.info(f'len(df_train) = {len(df_train)}')
logger.info(f'len(df_test) = {len(df_test)}')
df_train.to_csv(f"{mount_dir}/csv/train.csv", index=False)
df_test.to_csv(f"{mount_dir}/csv/test.csv", index=False)