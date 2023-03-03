import sys, os, glob, gc, copy, time, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'entity_linking/yolov5'))

# For data manipulation
import numpy as np
import pandas as pd
# Pytorch Imports
import torch
import torch.nn as nn
import torch.optim as optim
# Utils
from collections import defaultdict

# For colored terminal text
from colorama import Fore, Back, Style
b_ = Fore.BLUE
sr_ = Style.RESET_ALL
import warnings
warnings.filterwarnings("ignore")
# For descriptive error messages
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

from entity_linking.util import *
from entity_linking.data import *
from entity_linking.model import *
from entity_linking.train import *
# wandb
# %env "WANDB_NOTEBOOK_NAME" "pre_processing"
import wandb
wandb.login()

from omegaconf import OmegaConf
import hydra

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

# python 4_ml.py data.category=aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-4
def run_training(dataloaders, model, optimizer, scheduler, device, cfg, run, save_dir):
    logger.info(f'scheduler: {scheduler}')
    logger.info(f'optimizer: {optimizer}')

    if cfg.general.is_debug: num_epochs = cfg.train.epochs_debug
    else: num_epochs = cfg.train.epochs

    # To automatically log gradients
    wandb.watch(model, log_freq=100)
    
    if torch.cuda.is_available():
        print("[INFO] Using GPU: {}\n".format(torch.cuda.get_device_name()))
    
    dt_now = datetime.datetime.now()
    save_dir = f"../model/{cfg.data.category}/{str(dt_now.month).zfill(2)}{str(dt_now.day).zfill(2)}-{str(dt_now.hour).zfill(2)}{str(dt_now.minute).zfill(2)}{str(dt_now.second).zfill(2)}"
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"save_dir: {save_dir}")

    start = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_epoch_loss = np.inf
    history = defaultdict(list)
    for epoch in range(1, num_epochs + 1): 
        gc.collect()
        logger.info(f'epoch: {epoch}/{num_epochs}')
        logger.info(f'train step')
        train_epoch_loss, train_epoch_acc, train_epoch_precision_macro, train_epoch_precision_micro, train_epoch_recall_macro, train_epoch_recall_micro, train_epoch_f1_macro, train_epoch_f1_micro = \
          train_one_epoch(dataloaders["train"], model, criterion, optimizer, scheduler, device, \
                          n_accumulate = cfg.train.n_accumulate, \
                          enable_amp_half_precision=cfg.train.enable_amp_half_precision)
        logger.info(f'valid step')
        val_epoch_loss, val_epoch_acc, val_epoch_precision_macro, val_epoch_precision_micro, val_epoch_recall_macro, val_epoch_recall_micro, val_epoch_f1_macro, val_epoch_f1_micro = \
          valid_one_epoch(dataloaders["val"], model, criterion, device)
        l_names = ['Train Loss', 'Train Acc', 'Train Macro Precision', 'Train Micro Precision', 'Train Macro Recall', 'Train Micro Recall', 'Train Macro F1', 'Train Micro F1', 'Valid Loss', 'Valid Acc', 'Valid Macro Precision', 'Valid Micro Precision', 'Valid Macro Recall', 'Valid Micro Recall', 'Valid Macro F1', 'Valid Micro F1']
        l_vals = [train_epoch_loss, train_epoch_acc, train_epoch_precision_macro, train_epoch_precision_micro, train_epoch_recall_macro, train_epoch_recall_micro, train_epoch_f1_macro, train_epoch_f1_micro] + [val_epoch_loss, val_epoch_acc, val_epoch_precision_macro, val_epoch_precision_micro, val_epoch_recall_macro, val_epoch_recall_micro, val_epoch_f1_macro, val_epoch_f1_micro]
        for name, val in zip(l_names, l_vals):
          history[name].append(val)   
        # Log the metrics
        wandb.log({"Epoch": epoch})
        wandb.log({"LR": optimizer.param_groups[0]['lr']})
        for name, val in zip(l_names, l_vals):
          wandb.log({name: val})
        
        # deep copy the model
        if val_epoch_loss <= best_epoch_loss:
            print(f"{b_}Validation Loss Improved ({best_epoch_loss} ---> {val_epoch_loss})")
            best_epoch_loss = val_epoch_loss
            run.summary["Best Loss"] = best_epoch_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            PATH = f"{save_dir}/Loss{best_epoch_loss:.4f}_epoch{epoch:.0f}.bin"
            torch.save(model.state_dict(), PATH)
            # Save a model file from the current directory
            print(f"Model Saved{sr_}")
            
        print()
    
    end = time.time()
    time_elapsed = end - start
    logger.info('Training complete in {:.0f}h {:.0f}m {:.0f}s'.format(time_elapsed // 3600, (time_elapsed % 3600) // 60, (time_elapsed % 3600) % 60))
    logger.info("Best Loss: {:.4f}".format(best_epoch_loss))
    
    # load best model weights
    model.load_state_dict(best_model_wts)
    
    return model, history

def criterion(outputs, labels):
    return nn.CrossEntropyLoss()(outputs, labels)

@hydra.main(config_path="../conf/", config_name=f"config.yml")
def main(cfg: OmegaConf):
  logger.debug(f'cfg.data.batch_size["train"]: {cfg.data.batch_size["train"]}')
  logger.debug(f'cfg.data.batch_size.train: {cfg.data.batch_size.train}')

  # Seed
  device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  set_seed(cfg.general.seed)

  # Dataset
  category = cfg.data.category
  src_dir = f"../detect_{category}" # for cleaned data
  # src_dir = f"../../object_detection/data_{category}" # for original data
  # src_dir = f"../detect_{category}_debug" if is_debug else f"../detect_{category}"
  df_train = pd.read_csv(f"{src_dir}/csv/train.csv")

  data_transforms = GetTransforms(cfg.data.img_size)
  dataloaders = prepare_loaders(df_train, data_transforms, cfg.data.batch_size, fold=0)

  out_features = len(df_train['label'].unique())
  logger.info(f'out_features = {out_features}')

  model = EntityLinkingModel(cfg.model.model_name, out_features)
  model.to(device)

  optimizer = optim.Adam(model.parameters(), lr=cfg.optimizer.learning_rate, weight_decay=cfg.optimizer.weight_decay)
  scheduler = fetch_scheduler(optimizer, cfg.optimizer.scheduler, cfg.optimizer.T_max, cfg.optimizer.learning_rate*0.1)
  
  # For training
  run = wandb.init(project='EntityLinking', config=OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True))
  model, history = run_training(dataloaders, model, optimizer, scheduler, device, cfg, run, category)
  run.finish()

  # For visualizing results
  # model.load_state_dict(torch.load("../model/Loss0.0488_epoch10.bin"))
  # model.eval()
  # visualize_model(dataloaders, model, device)

if __name__ == '__main__':
  main()
