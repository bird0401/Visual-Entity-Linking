import gc
from tqdm import tqdm
import torch
from torch.optim import lr_scheduler
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

def train_one_epoch(model, optimizer, scheduler, dataloader, device, epoch, n_accumulate, criterion, enable_amp_half_precision):
  try:
    model.train()
    
    dataset_size = 0
    running_loss = 0.0

    all_labels = []
    all_preds = []
    
    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:
        images = data['image'].to(device, dtype=torch.float)
        labels = data['label'].to(device, dtype=torch.long)
        
        batch_size = images.size(0)
        
        outputs = model(images, labels)
        loss = criterion(outputs, labels)
        loss = loss / n_accumulate
        loss.backward()

        if (step + 1) % n_accumulate == 0:
            optimizer.step()
            optimizer.zero_grad()
            if scheduler is not None:
                scheduler.step()
            
        predicted = torch.max(outputs, 1)[1]
        running_loss += (loss.item() * batch_size)
        all_labels.extend(labels.cpu().detach().numpy().copy())
        all_preds.extend(predicted.cpu().detach().numpy().copy())
        dataset_size += batch_size
        epoch_loss = running_loss / dataset_size

    gc.collect()
    return epoch_loss, accuracy_score(all_labels, all_preds), precision_score(all_labels, all_preds, average='macro'), recall_score(all_labels, all_preds, average='macro'), f1_score(all_labels, all_preds, average='macro')
  
  except:
    import traceback
    traceback.print_exc()

@torch.inference_mode()
def valid_one_epoch(model, dataloader, device, epoch, criterion, optimizer):
  try:
    model.eval()
    
    dataset_size = 0
    running_loss = 0.0
    all_labels = []
    all_preds = []
    
    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:        
        images = data['image'].to(device, dtype=torch.float)
        labels = data['label'].to(device, dtype=torch.long)
        
        batch_size = images.size(0)

        outputs = model(images, labels)
        loss = criterion(outputs, labels)
        
        predicted = torch.max(outputs, 1)[1]
        running_loss += (loss.item() * batch_size)
        all_labels.extend(labels.cpu().detach().numpy().copy())
        all_preds.extend(predicted.cpu().detach().numpy().copy())
        dataset_size += batch_size
        epoch_loss = running_loss / dataset_size
    
    gc.collect()
    return epoch_loss, accuracy_score(all_labels, all_preds), precision_score(all_labels, all_preds, average='macro'), recall_score(all_labels, all_preds, average='macro'), f1_score(all_labels, all_preds, average='macro')
  
  except:
    import traceback
    traceback.print_exc()


def fetch_scheduler(optimizer, scheduler, T_max, T_0, min_lr):
    if scheduler == 'CosineAnnealingLR':
        scheduler = lr_scheduler.CosineAnnealingLR(optimizer,T_max=T_max, 
                                                   eta_min=min_lr)
    elif scheduler == 'CosineAnnealingWarmRestarts':
        scheduler = lr_scheduler.CosineAnnealingWarmRestarts(optimizer,T_0=T_0, 
                                                             eta_min=min_lr)
    elif scheduler == None:
        return None
        
    return scheduler
