import os, traceback, glob, time
from collections import defaultdict
import numpy as np
import torch
from PIL import Image, ImageOps, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True
from colorama import Fore, Back, Style
b_ = Fore.BLUE
sr_ = Style.RESET_ALL
import warnings
warnings.filterwarnings("ignore")
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

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

# delete all exif data
def delete_exif(path):
    try:
        src = Image.open(path)
        dst = Image.new(src.mode, src.size)
        dst.putdata(src.getdata())
        dst.convert('RGB').save(path)
    except UnidentifiedImageError:
        print(f"remove {path}")
        os.remove(path)
    except Exception:
        print(path)
        traceback.print_exc()

# fetch hashtable from file name to their bounding boxes
def fetch_crops(results):
    crops = defaultdict(list)
    for i, (im, pred) in enumerate(zip(results.ims, results.pred)):
        if pred.shape[0]:
            for *box, conf, cls in reversed(pred):  # xyxy, confidence, class
              crops[results.files[i]].append(box)
    return crops