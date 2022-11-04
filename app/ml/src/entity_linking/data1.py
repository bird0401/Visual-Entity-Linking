import cv2
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset
import traceback    

def GetTransforms(input_size, color_mean = [0.485, 0.456, 0.406], color_std = [0.229, 0.224, 0.225]):
    data_transforms = {
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
    
    return data_transforms

data_transforms = {
    "train": A.Compose([
        A.Resize(CONFIG['img_size'], CONFIG['img_size']),
        A.HorizontalFlip(p=0.5),
        A.HueSaturationValue(always_apply=False, hue_shift_limit=(-20, 20), sat_shift_limit=(-30, 30), val_shift_limit=(-20, 20), p=0.5),
#        A.ShiftScaleRotate(always_apply=False, shift_limit=(-0.10999999940395355, 0.10999999940395355), scale_limit=(-0.5899999737739563, -0.28999999165534973), rotate_limit=(-26, 24), interpolation=0, border_mode=0, value=(0, 0, 0), mask_value=None, p=0.5),
#        A.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.3, always_apply=False, p=0.5),
        A.Blur(blur_limit=7, p=0.5),
#        A.Cutout(num_holes=8, max_h_size=32, max_w_size=32, fill_value=0, always_apply=False, p=0.5),
        A.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225], 
                max_pixel_value=255.0, 
                p=1.0
            ),
        ToTensorV2()], p=1.),
    
    "valid": A.Compose([
        A.Resize(CONFIG['img_size'], CONFIG['img_size']),
        A.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225], 
                max_pixel_value=255.0, 
                p=1.0
            ),
        ToTensorV2()], p=1.)
}


cfg.train_aug = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.ImageCompression(quality_lower=99, quality_upper=100),
        A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=10, border_mode=0, p=0.7),
        A.Resize(image_size, image_size),
        A.Cutout(max_h_size=int(image_size * 0.4), max_w_size=int(image_size * 0.4), num_holes=1, p=0.5),
    ])

cfg.val_aug = A.Compose([A.Resize(image_size, image_size),])

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

