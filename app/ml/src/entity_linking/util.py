import os
import matplotlib.pyplot as plt
import numpy as np
import torch

import logging
import logging.config
from yaml import safe_load
with open('../../conf/logging.yml') as f:
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

def visualize_model(dataloaders, model, device, num_images=50, was_training=False):
    was_training = model.training
    model.eval()
    images_so_far = 0
    plt.figure(figsize=(20, 15))
    
    res_dir = "./results"
    res_path = res_dir + "/preds.png"
    os.makedirs(res_dir, exist_ok=False)

    with torch.no_grad():
        for i, data in enumerate(dataloaders['val']):
            images = data['image'].to(device, dtype=torch.float)
            labels = data['label'].to(device, dtype=torch.long)

            outputs = model(images, labels)
            _, preds = torch.max(outputs, 1)

            for j in range(images.size()[0]):
                images_so_far += 1
                logger.debug(f"images_so_far: {images_so_far}")
                ax = plt.subplot(5, 10, images_so_far)
                ax.axis('off')
                ax.set_title(f'{preds[j]}:{labels[j]}', fontsize=16)
                imshow(images.cpu().data[j], ax)

                if images_so_far == num_images:
                    plt.savefig(res_path)
                    return
        plt.savefig(res_path)