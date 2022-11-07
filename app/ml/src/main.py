import os, gc, math, copy, time, random, joblib, yaml, traceback
# For data manipulation
import numpy as np
import pandas as pd
import cv2
# Pytorch Imports
import torch
import torch.nn as nn
import torch.optim as optim
# Utils
from tqdm import tqdm
from collections import defaultdict
from pathlib import Path
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

from omegaconf import DictConfig, OmegaConf
import hydra

import logging
import logging.config
from yaml import safe_load
with open('../conf/logging.yml') as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger('main')

# Configuration and Seed
# with open("../config.yml", "r") as yml:
#     cfg = yaml.safe_load(yml)
# cfg["device"] = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# set_seed(cfg['seed'])

def run_training(dataloaders, model, optimizer, scheduler, device, cfg, run):
    if cfg.general.debug: num_epochs = cfg.train.epochs_debug
    else: num_epochs = cfg.train.epochs

    # To automatically log gradients
    wandb.watch(model, log_freq=100)
    
    if torch.cuda.is_available():
        print("[INFO] Using GPU: {}\n".format(torch.cuda.get_device_name()))
    
    start = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_epoch_loss = np.inf
    history = defaultdict(list)
    
    for epoch in range(1, num_epochs + 1): 
        gc.collect()
        logger.info(f'epoch = {epoch}')
        train_epoch_loss, train_epoch_acc, train_epoch_precision, train_epoch_recall, train_epoch_f1 = \
          train_one_epoch(dataloaders["train"], model, criterion, optimizer, scheduler, device, \
                          n_accumulate = cfg.train.n_accumulate, \
                          enable_amp_half_precision=cfg.train.enable_amp_half_precision)
        val_epoch_loss, val_epoch_acc, val_epoch_precision, val_epoch_recall, val_epoch_f1 = \
          valid_one_epoch(dataloaders["val"], model, criterion, device)

        l_names = ['Train Loss', 'Train Acc', 'Train Precision', 'Train Recall', 'Train F1', 'Valid Loss', 'Valid Acc', 'Valid Precision', 'Valid Recall', 'Valid F1']
        l_vals = [train_epoch_loss, train_epoch_acc, train_epoch_precision, train_epoch_recall, train_epoch_f1] + [val_epoch_loss, val_epoch_acc, val_epoch_precision, val_epoch_recall, val_epoch_f1]

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
            PATH = "../model/Loss{:.4f}_epoch{:.0f}.bin".format(best_epoch_loss, epoch)
            torch.save(model.state_dict(), PATH)
            # Save a model file from the current directory
            print(f"Model Saved{sr_}")
            
        print()
    
    end = time.time()
    time_elapsed = end - start
    print('Training complete in {:.0f}h {:.0f}m {:.0f}s'.format(time_elapsed // 3600, (time_elapsed % 3600) // 60, (time_elapsed % 3600) % 60))
    print("Best Loss: {:.4f}".format(best_epoch_loss))
    
    # load best model weights
    model.load_state_dict(best_model_wts)
    
    return model, history

def criterion(outputs, labels):
    return nn.CrossEntropyLoss()(outputs, labels)

@hydra.main(config_path="../conf/", config_name="config.yml")
def main(cfg: OmegaConf):
  # logger.debug(f'cfg.data.batch_size["train"]: {cfg.data.batch_size["train"]}')
  logger.debug(f'cfg.data.batch_size["train"]: {cfg.data.batch_size.train}')
  
  # Seed
  device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  set_seed(cfg.general.seed)

  # Dataset
  if cfg.general.debug: df_train = pd.read_csv("../data/csv/train_debug.csv")
  else: df_train = pd.read_csv("../data/csv/train.csv")
  data_transforms = GetTransforms(cfg.data.img_size)
  # if cfg.general.debug: train_loader, valid_loader = prepare_loaders(EntityLinkingDataset, data_transforms, cfg.data.train_batch_size_debug, cfg.data.valid_batch_size_debug, df_train, fold=0)
  # else: train_loader, valid_loader = prepare_loaders(EntityLinkingDataset, data_transforms, cfg.data.train_batch_size, cfg.data.valid_batch_size, df_train, fold=0)
  if cfg.general.debug: dataloaders = prepare_loaders(df_train, data_transforms, cfg.data.batch_size_debug, fold=0)
  else: dataloaders = prepare_loaders(df_train, data_transforms, cfg.data.batch_size, fold=0)

  out_features = len(df_train['label'].unique())
  logger.info(f'out_features = {out_features}')

  model = EntityLinkingModel(cfg.model.model_name, out_features)
  model.to(device)

  optimizer = optim.Adam(model.parameters(), lr=cfg.optimizer.learning_rate, weight_decay=cfg.optimizer.weight_decay)
  scheduler = fetch_scheduler(optimizer, cfg.optimizer.scheduler, cfg.optimizer.T_max, cfg.optimizer.T_0, cfg.optimizer.min_lr)

  run = wandb.init(project='EntityLinking', config=OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True))
  model, history = run_training(dataloaders, model, optimizer, scheduler, device, cfg, run)
  run.finish()

if __name__ == '__main__':
  main()
