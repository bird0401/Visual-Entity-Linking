import os, pickle
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from entity_linking.yolov5.utils.plots import Annotator

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('util')

def set_seed(seed=42):
    '''Sets the seed of the entire notebook so results are the same every time we run.
    This is for REPRODUCIBILITY.'''
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # When running on the CuDNN backend, two further options must be set
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    # Set a fixed value for the hash seed
    os.environ['PYTHONHASHSEED'] = str(seed)

def tensor2np(inp):
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    return inp

def imshow(inp, ax):
    inp = tensor2np(inp)
    ax.imshow(inp)
    # plt.pause(0.001)  # pause a bit so that plots are updated

def annotate_save(img_path, crops_info, wikidata_id, file_name, label = "0", labels = True, save_dir = "save_dir"):
  boxes = crops_info[wikidata_id][file_name]
  if boxes: 
    im = np.array(Image.open(img_path))
    annotator = Annotator(im, example="dog")
    for box in boxes:
      annotator.box_label(box, label if labels else '', color = (0, 255, 0))
    im = annotator.im
    pil_img = Image.fromarray(im)
    os.makedirs(f'{save_dir}/{wikidata_id}', exist_ok=True)
    pil_img.save(f'{save_dir}/{wikidata_id}/{file_name}')

def visualize_model(dataloaders, model, device, num_images=50, was_training=False):
    model.eval()
    images_so_far = 0
    with open(f"../data/detect/crops_info.pickle", 'rb') as f:
      crops_info = pickle.load(f)
    with torch.no_grad():
        for i, data in enumerate(dataloaders['val']):
            images = data['image'].to(device, dtype=torch.float)
            labels = data['label'].to(device, dtype=torch.long)
            file_paths = data['file_path']
            file_noncrop_paths = data['file_noncrop_path']
            wikidata_id = data['wikidata_id']
            file_name = data['file_name']

            outputs = model(images, labels)
            _, preds = torch.max(outputs, 1)

            for j in range(images.size()[0]):
                images_so_far += 1
                logger.debug(f"images_so_far: {images_so_far}")
                annotated = annotate_save(img_path=file_noncrop_paths[j], crops_info=crops_info, wikidata_id=wikidata_id[j], file_name=file_name[j], label=f'{labels[j]} : {preds[j]}')
                if images_so_far == num_images:
                    logger.debug(f"images_so_far: {images_so_far}")
                    return
    