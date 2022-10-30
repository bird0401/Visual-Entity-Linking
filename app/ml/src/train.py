from tqdm import tqdm
import torch
import gc
from torch.optim import lr_scheduler
import torch.amp

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

def train_one_epoch(model, optimizer, scheduler, dataloader, device, epoch, n_accumulate, criterion, enable_amp_half_precision):
    model.train()
    
    dataset_size = 0
    running_loss = 0.0
    running_acc = 0.0
    running_recall = 0.0
    running_f1 = 0.0
    
    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:
        images = data['image'].to(device, dtype=torch.float)
        labels = data['label'].to(device, dtype=torch.long)
        
        batch_size = images.size(0)
        
        outputs = model(images, labels)
        loss = criterion(outputs, labels)
        loss = loss / n_accumulate

        # if enable_amp_half_precision:
        #     with amp.scale_loss(loss, optimizer) as scaled_loss:
        #         scaled_loss.backward()
        # else:
        
        loss.backward()

        if (step + 1) % n_accumulate == 0:
            optimizer.step()
            optimizer.zero_grad()
            if scheduler is not None:
                scheduler.step()
            
        predicted = torch.max(outputs, 1)[1]
        running_loss += (loss.item() * batch_size)
        running_acc += accuracy_score(labels, predicted)
        running_recall += recall_score(labels, predicted)
        running_f1 += f1_score(labels, predicted, average='macro')
        
        dataset_size += batch_size
        epoch_loss = running_loss / dataset_size
        epoch_acc = running_acc / dataset_size
        epoch_recall = running_recall / dataset_size
        epoch_f1 = running_f1 / dataset_size        
        
        # show each values on the progress bar
        bar.set_postfix(Epoch=epoch, Train_Loss=epoch_loss, Train_Acc=epoch_acc,
                        LR=optimizer.param_groups[0]['lr'])
    gc.collect()
    
    return epoch_loss, epoch_acc, epoch_recall, epoch_f1

@torch.inference_mode()
def valid_one_epoch(model, dataloader, device, epoch, criterion, optimizer):
    model.eval()
    
    dataset_size = 0
    running_loss = 0.0
    running_acc = 0.0
    running_recall = 0.0
    running_f1 = 0.0
    
    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:        
        images = data['image'].to(device, dtype=torch.float)
        labels = data['label'].to(device, dtype=torch.long)
        
        batch_size = images.size(0)

        outputs = model(images, labels)
        loss = criterion(outputs, labels)
        
        predicted = torch.max(outputs, 1)[1]
        running_loss += (loss.item() * batch_size)
        running_acc += accuracy_score(labels, predicted)
        running_recall += recall_score(labels, predicted)
        running_f1 += f1_score(labels, predicted, average='macro')

        dataset_size += batch_size
        epoch_loss = running_loss / dataset_size
        epoch_acc = running_acc / dataset_size
        epoch_recall = running_recall / dataset_size
        epoch_f1 = running_f1 / dataset_size 
        
        bar.set_postfix(Epoch=epoch, Valid_Loss=epoch_loss, Valid_Acc=epoch_acc,
                        LR=optimizer.param_groups[0]['lr'])   
    
    gc.collect()
    
    return epoch_loss, epoch_acc, epoch_recall, epoch_f1


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