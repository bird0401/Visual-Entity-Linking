import gc, traceback
from tqdm import tqdm
import torch
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("train")


def scores(labels, preds):
    assert labels, labels
    assert labels, preds
    acc = accuracy_score(labels, preds)
    precision_macro = precision_score(labels, preds, average="macro")
    precision_micro = precision_score(labels, preds, average="micro")
    recall_macro = recall_score(labels, preds, average="macro")
    recall_micro = recall_score(labels, preds, average="micro")
    f1_macro = f1_score(labels, preds, average="macro")
    f1_micro = f1_score(labels, preds, average="micro")

    assert 0 <= acc <= 1, f"acc is {acc}"
    assert 0 <= precision_macro <= 1, f"precision_macro is {precision_macro}"
    assert 0 <= precision_micro <= 1, f"precision_micro is {precision_micro}"
    assert 0 <= recall_macro <= 1, f"recall_macro is {recall_macro}"
    assert 0 <= recall_micro <= 1, f"recall_micro is {recall_micro}"
    assert 0 <= f1_macro <= 1, f"f1_macro is {f1_macro}"
    assert 0 <= f1_micro <= 1, f"f1_micro is {f1_micro}"

    return (
        acc,
        precision_macro,
        precision_micro,
        recall_macro,
        recall_micro,
        f1_macro,
        f1_micro,
    )


def train_one_epoch(
    dataloader, model, criterion, optimizer, scheduler, device, n_accumulate, enable_amp_half_precision,
):
    logger.info("train_one_epoch")
    try:
        model.train()
        dataset_size = 0
        running_loss = 0.0
        all_labels = []
        all_preds = []

        for step, data in tqdm(enumerate(dataloader), total=len(dataloader)):
            images = data["image"].to(device, dtype=torch.float)
            labels = data["label"].to(device, dtype=torch.long)
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
            running_loss += loss.item() * batch_size
            all_labels.extend(labels.to("cpu").detach().numpy().copy())
            all_preds.extend(predicted.to("cpu").detach().numpy().copy())
            dataset_size += batch_size
            epoch_loss = running_loss / dataset_size

        (acc, precision_macro, precision_micro, recall_macro, recall_micro, f1_macro, f1_micro,) = scores(all_labels, all_preds)
        gc.collect()
        return (
            epoch_loss,
            acc,
            precision_macro,
            precision_micro,
            recall_macro,
            recall_micro,
            f1_macro,
            f1_micro,
        )

    except Exception:
        traceback.print_exc()


@torch.inference_mode()
def valid_one_epoch(dataloader, model, criterion, device):
    logger.info("valid_one_epoch")
    assert len(dataloader) > 0, f"len(dataloader): {len(dataloader)}"
    try:
        model.eval()
        dataset_size = 0
        running_loss = 0.0
        all_labels = []
        all_preds = []

        for step, data in tqdm(enumerate(dataloader), total=len(dataloader)):
            images = data["image"].to(device, dtype=torch.float)
            labels = data["label"].to(device, dtype=torch.long)

            batch_size = images.size(0)
            outputs = model(images, labels)
            loss = criterion(outputs, labels)

            predicted = torch.max(outputs, 1)[1]
            running_loss += loss.item() * batch_size
            all_labels.extend(labels.to("cpu").detach().numpy().copy())
            all_preds.extend(predicted.to("cpu").detach().numpy().copy())
            dataset_size += batch_size
            epoch_loss = running_loss / dataset_size

        (acc, precision_macro, precision_micro, recall_macro, recall_micro, f1_macro, f1_micro,) = scores(all_labels, all_preds)
        gc.collect()
        return (
            epoch_loss,
            acc,
            precision_macro,
            precision_micro,
            recall_macro,
            recall_micro,
            f1_macro,
            f1_micro,
        )

    except Exception:
        traceback.print_exc()


# @torch.inference_mode()
# def test_one_epoch(dataloader, model, device):
#     logger.info("test_one_epoch")
#     assert len(dataloader) > 0, f"len(dataloader): {len(dataloader)}"
#     try:
#         model.eval()
#         dataset_size = 0
#         all_labels = []
#         all_preds = []

#         for step, data in tqdm(enumerate(dataloader), total=len(dataloader)):
#             images = data["image"].to(device, dtype=torch.float)
#             labels = data["label"].to(device, dtype=torch.long)

#             batch_size = images.size(0)
#             outputs = model(images, labels)

#             predicted = torch.max(outputs, 1)[1]
#             all_labels.extend(labels.to("cpu").detach().numpy().copy())
#             all_preds.extend(predicted.to("cpu").detach().numpy().copy())
#             dataset_size += batch_size

#         (
#             acc,
#             precision_macro,
#             precision_micro,
#             recall_macro,
#             recall_micro,
#             f1_macro,
#             f1_micro,
#         ) = scores(all_labels, all_preds)
#         gc.collect()
#         return (
#             acc,
#             precision_macro,
#             precision_micro,
#             recall_macro,
#             recall_micro,
#             f1_macro,
#             f1_micro,
#         )

# except Exception:
#     traceback.print_exc()


# def fetch_scheduler(optimizer, scheduler, T_max, min_lr, T_0=None):
#     if scheduler == "CosineAnnealingLR":
#         scheduler = lr_scheduler.CosineAnnealingLR(
#             optimizer, T_max=T_max, eta_min=min_lr
#         )
#     elif scheduler == "CosineAnnealingWarmRestarts":
#         scheduler = lr_scheduler.CosineAnnealingWarmRestarts(
#             optimizer, T_0=T_0, eta_min=min_lr
#         )
#     elif scheduler == None:
#     logger.info(f"scheduler = {scheduler}")
#     return scheduler
