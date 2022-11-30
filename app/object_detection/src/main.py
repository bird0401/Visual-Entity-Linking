import glob
from yolo_detection.utils import *
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
set_seed(2022) # TODO 

model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)
model.classes = [16] # predict only dog
model.to(device)

img_dir = "/content/Instance_level_recognition/app/ml/data/imgs"
imgs = glob.glob(img_dir + '/*/*')

results = model(imgs)
results.print()