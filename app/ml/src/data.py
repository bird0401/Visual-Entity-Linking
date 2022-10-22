from torch.utils.data import Dataset
import cv2
import torch
import traceback    

class EntityLinkingDataset(Dataset):
    def __init__(self, df, transforms=None):
        self.df = df
        # self.file_names = df['file_path'].values
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