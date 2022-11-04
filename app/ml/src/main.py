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

# Configuration and Seed
with open("../config.yml", "r") as yml:
    CONFIG = yaml.safe_load(yml)
CONFIG["device"] = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
set_seed(CONFIG['seed'])

# Dataset
if CONFIG["debug"]: df_train = pd.read_csv("../data/csv/train_debug.csv")
else: df_train = pd.read_csv("../data/csv/train.csv")
CONFIG["num_classees"] = CONFIG["out_features"] = len(df_train['label'].unique())
data_transforms = GetTransforms(CONFIG['img_size'])
train_loader, valid_loader = prepare_loaders(EntityLinkingDataset, data_transforms, CONFIG['train_batch_size'], CONFIG['valid_batch_size'], df_train, fold=0)


def criterion(outputs, labels):
    return nn.CrossEntropyLoss()(outputs, labels)

def run_training(run, model, optimizer, scheduler, device, num_epochs):
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
        train_epoch_loss, train_epoch_acc, train_epoch_precision, train_epoch_recall, train_epoch_f1 = train_one_epoch(model, optimizer, scheduler, 
                                           dataloader=train_loader, 
                                           device=CONFIG['device'], epoch=epoch, n_accumulate = CONFIG['n_accumulate'], criterion = criterion,
                                           enable_amp_half_precision=CONFIG['enable_amp_half_precision'])
        val_epoch_loss, val_epoch_acc, val_epoch_precision, val_epoch_recall, val_epoch_f1 = valid_one_epoch(model, valid_loader, device=CONFIG['device'], 
                                         epoch=epoch, criterion=criterion, optimizer=optimizer)
        

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
            PATH = "Loss{:.4f}_epoch{:.0f}.bin".format(best_epoch_loss, epoch)
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


if __name__ == '__main__':
  model = EntityLinkingModel(CONFIG['model_name'], CONFIG['out_features'])
  model.to(CONFIG['device'])
  optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'], weight_decay=CONFIG['weight_decay'])
  scheduler = fetch_scheduler(optimizer, CONFIG['scheduler'], CONFIG['T_max'], CONFIG['T_0'], CONFIG['min_lr'])

  run = wandb.init(project='EntityLinking', config=CONFIG)

  if CONFIG["debug"]:
    model, history = run_training(run, model, optimizer, scheduler, device=CONFIG['device'], num_epochs=CONFIG['epochs_debug'])
  else:
    model, history = run_training(run, model, optimizer, scheduler, device=CONFIG['device'], num_epochs=CONFIG['epochs'])

  run.finish()