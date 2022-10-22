import albumentations as A
from albumentations.pytorch import ToTensorV2

from torch.utils.data import Dataset
import cv2
import torch
import traceback    

def GetTransform(input_size, color_mean = [0.485, 0.456, 0.406], color_std = [0.229, 0.224, 0.225], phase = "train"):
    data_transform = {
        "train": A.Compose([
            A.Resize(input_size, input_size),
            A.ShiftScaleRotate(shift_limit=0.1, 
                            scale_limit=0.15, 
                            rotate_limit=60, 
                            p=0.5),
            A.HueSaturationValue(
                    hue_shift_limit=0.2, 
                    sat_shift_limit=0.2, 
                    val_shift_limit=0.2, 
                    p=0.5
                ),
            A.RandomBrightnessContrast(
                    brightness_limit=(-0.1,0.1), 
                    contrast_limit=(-0.1, 0.1), 
                    p=0.5
                ),
            A.Normalize(
                    mean=color_mean, 
                    std=color_std, 
                    max_pixel_value=255.0, 
                    p=1.0
                ),
            ToTensorV2()], p=1.),
        
        "valid": A.Compose([
            A.Resize(input_size, input_size),
            A.Normalize(
                    mean=color_mean, 
                    std=color_std, 
                    max_pixel_value=255.0, 
                    p=1.0
                ),
            ToTensorV2()], p=1.)
    }
    
    return data_transform[phase]


class EntityLinkingDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df
        # self.file_names = df['file_path'].values
        self.file_names = df['path'].values
        self.labels = df['label'].values
        self.transform = transform
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, index):
      try:
        img_path = self.file_names[index]
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        label = self.labels[index]
        
        if self.transform:
            img = self.transform(image=img)
            
        return {
            'image': img,
            'label': torch.tensor(label, dtype=torch.long)
        }
      except Exception: 
        print()
        print(f"img_path: {img_path}")
        traceback.print_exc()
        return None