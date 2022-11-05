import cv2
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset, DataLoader
import traceback    

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
        
        "valid": A.Compose([
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

def prepare_loaders(my_Dataset, transforms, train_batch_size, valid_batch_size, df, fold):
    assert type(my_Dataset) is EntityLinkingDataset, f"type(my_Dataset) is {type(my_Dataset)}"
    assert transforms["train"]
    assert transforms["valid"]
    assert 0 <= fold <= 4
    
    df_train = df[df.kfold != fold].reset_index(drop=True)
    df_valid = df[df.kfold == fold].reset_index(drop=True)

    assert df_train
    assert df_valid
    
    train_dataset = my_Dataset(df_train, transforms=transforms["train"])
    valid_dataset = my_Dataset(df_valid, transforms=transforms["valid"])

    train_loader = DataLoader(train_dataset, batch_size=train_batch_size, 
                            num_workers=2, collate_fn = collate_fn, shuffle=True, pin_memory=True, drop_last=True)
    valid_loader = DataLoader(valid_dataset, batch_size=valid_batch_size, 
                                num_workers=2, collate_fn = collate_fn, shuffle=False, pin_memory=True)
    return train_loader, valid_loader
