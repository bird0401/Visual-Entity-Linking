import cv2
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset, DataLoader
import traceback   

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('data')
    

def GetTransforms(input_size, color_mean = [0.485, 0.456, 0.406], color_std = [0.229, 0.224, 0.225]):
    data_transforms = {
        "train": A.Compose([
            A.HorizontalFlip(p=0.5),
            A.ImageCompression(quality_lower=99, quality_upper=100),
            A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=10, border_mode=0, p=0.7),
            A.Resize(input_size, input_size),
            A.Cutout(max_h_size=int(input_size * 0.4), max_w_size=int(input_size * 0.4), num_holes=1, p=0.5),
            A.Normalize(mean=color_mean, std=color_std, max_pixel_value=255.0, p=1.0),
            ToTensorV2()], p=1.),
        
        "val": A.Compose([
            A.Resize(input_size, input_size),
            A.Normalize(mean=color_mean, std=color_std, max_pixel_value=255.0, p=1.0),
            ToTensorV2()], p=1.)
    }
    
    return data_transforms


class EntityLinkingDataset(Dataset):
    def __init__(self, df, transforms=None):
        self.df = df
        self.file_names = df['path'].values
        self.labels = df['label'].values
        self.transforms = transforms
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, index):
      try:
        img_path = self.file_names[index]
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        label = self.labels[index]
        
        if self.transforms:
            img = self.transforms(image=img)["image"]
            
        return {
            'image': img,
            'label': torch.tensor(label, dtype=torch.long)
        }
      except Exception: 
        print()
        print(f"img_path: {img_path}")
        traceback.print_exc()
        return None

def collate_fn(batch):
    batch = list(filter(lambda x: x is not None, batch))
    return torch.utils.data.dataloader.default_collate(batch)

def prepare_loaders(df, transforms, batch_size, fold):
    assert transforms["train"]
    assert transforms["val"]
    assert batch_size["train"]
    assert batch_size["val"]
    assert 0 <= fold <= 4
    
    df_train_val = {
        "train": df[df.kfold != fold].reset_index(drop=True),
        "val": df[df.kfold == fold].reset_index(drop=True)
    }

    assert not df_train_val["train"].empty
    assert not df_train_val["val"].empty

    logger.info(f'len(df_train_val["train"]) = {len(df_train_val["train"])}')
    logger.info(f'len(df_train_val["val"]) = {len(df_train_val["val"])}')
    
    datasets = {
        x: EntityLinkingDataset(df_train_val[x], transforms=transforms[x])
        for x in ["train", "val"]
    }

    dataloaders = {
        x: DataLoader(datasets[x], batch_size=batch_size[x], num_workers=2, collate_fn = collate_fn, shuffle=(x == "train"), pin_memory=True, drop_last=True)
        for x in ["train", "val"]
    }
  
    return dataloaders
