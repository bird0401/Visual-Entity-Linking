import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image

def albumentations_transform(image):   
    a_transform=GetTransforms(cfg.data.img_size)["train"]
    return a_transform(image=np.array(image))['image']

data_transforms = transforms.Compose([
    transforms.Lambda(albumentations_transform),
])

train_dir="/content/Instance_level_recognition/app/ml/data/imgs"
dataset_augmentated = datasets.ImageFolder(root=train_dir, transform=data_transforms)