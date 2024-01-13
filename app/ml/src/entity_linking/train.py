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


def calculate_topk_accuracy(outputs, labels, top_k=1):
    _, indices = torch.topk(outputs, top_k, dim=1)
    correct_topk = torch.sum(torch.eq(indices, labels.view(-1, 1)).any(dim=1))
    return correct_topk.item() / labels.size(0)


# TODO: TOP-K accuracy
# 画像認識→
# 現状
# それぞれのidごとにoracleと仮のprediction idでTOP-1を計算している

# これをTOP-Kに変更
# - oracleでは変更の必要はなし
# - w/o oracleでは、仮のprediction idをTOP-Kに変更する必要がある

# さらに、仮のprediction idであるため、これを実際のprediction idとする必要があり、このためにここでの出力結果を用いる
# そのためには、それぞれのidごとに、TOP-Kのprediction idを出力する必要がある

# 今まではidごとに回答していたため意識する必要はなかったが、画像が複数ある場合には、それぞれの画像ごとの回答が必要となる
# そのため、idの中の画像ごとのid予測結果を出力する必要があるが、計算時間がかかるため、今回は予測結果のうちどれか1つのみを用いて出力する
# この条件下では、それぞれのidごとの1枚の画像をテストに用いるのがMLにおいても計算時間を短縮できるため良いが、その実装も面倒であるため今回は割愛する


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
def valid_one_epoch(dataloader, model, criterion, device, top_k=20):
    logger.info("valid_one_epoch")
    assert len(dataloader) > 0, f"len(dataloader): {len(dataloader)}"
    try:
        model.eval()
        dataset_size = 0
        running_loss = 0.0
        # correct_topk = 0
        correct_top1, correct_top2, correct_top3, correct_top5, correct_top10, correct_top20 = 0, 0, 0, 0, 0, 0
        all_labels = []
        all_preds = []
        # all_indices = []  # List to store top-k indices
        # all_confidences = []  # List to store confidence scores
        id_indices_confidences_dict = {}  # Dictionary to store correct ID, top-k indices, and confidence scores

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

            # Calculate top-k indices and confidence scores
            values, indices = torch.topk(outputs, top_k, dim=1)
            confidence_scores = torch.softmax(values, dim=1)

            # Check top-1, 2, 3, 5, 10, 20 accuracy
            # correct_topk += torch.sum(torch.eq(indices, labels.view(-1, 1))).item()
            correct_top1 += torch.sum(torch.eq(indices[:, :1], labels.view(-1, 1))).item()
            correct_top2 += torch.sum(torch.eq(indices[:, :2], labels.view(-1, 1))).item()
            correct_top3 += torch.sum(torch.eq(indices[:, :3], labels.view(-1, 1))).item()
            correct_top5 += torch.sum(torch.eq(indices[:, :5], labels.view(-1, 1))).item()
            correct_top10 += torch.sum(torch.eq(indices[:, :10], labels.view(-1, 1))).item()
            correct_top20 += torch.sum(torch.eq(indices[:, :20], labels.view(-1, 1))).item()

            # all_indices.extend(indices.to("cpu").detach().numpy().copy())
            # all_confidences.extend(confidence_scores.to("cpu").detach().numpy().copy())
            # Convert to standard Python lists
            indices_list = indices.to("cpu").detach().numpy().tolist()
            confidences_list = confidence_scores.to("cpu").detach().numpy().tolist()

            # Store correct ID, top-k indices, and confidence scores in the dictionary
            for idx, label in enumerate(labels):
                correct_id = label.item()
                if correct_id not in id_indices_confidences_dict:
                    id_indices_confidences_dict[correct_id] = {"indices": [], "confidences": []}

                id_indices_confidences_dict[correct_id]["indices"].append(indices_list[idx])
                id_indices_confidences_dict[correct_id]["confidences"].append(confidences_list[idx])


        # topk_accuracy = correct_topk / dataset_size
        top1_accuracy = correct_top1 / dataset_size
        top2_accuracy = correct_top2 / dataset_size
        top3_accuracy = correct_top3 / dataset_size
        top5_accuracy = correct_top5 / dataset_size
        top10_accuracy = correct_top10 / dataset_size
        top20_accuracy = correct_top20 / dataset_size

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
            # topk_accuracy,
            top1_accuracy,
            top2_accuracy,
            top3_accuracy,
            top5_accuracy,
            top10_accuracy,
            top20_accuracy,
            id_indices_confidences_dict,
            # all_indices,
            # all_confidences,
            # all_indices[:top_k],  # Return top-k indices
            # all_confidences[:top_k],  # Return only the confidence scores for TOP-K predictions
        )

    except Exception:
        traceback.print_exc()


# @torch.inference_mode()
# def valid_one_epoch(dataloader, model, criterion, device):
#     logger.info("valid_one_epoch")
#     assert len(dataloader) > 0, f"len(dataloader): {len(dataloader)}"
#     try:
#         model.eval()
#         dataset_size = 0
#         running_loss = 0.0
#         all_labels = []
#         all_preds = []

#         for step, data in tqdm(enumerate(dataloader), total=len(dataloader)):
#             images = data["image"].to(device, dtype=torch.float)
#             labels = data["label"].to(device, dtype=torch.long)

#             batch_size = images.size(0)
#             outputs = model(images, labels)
#             loss = criterion(outputs, labels)

#             predicted = torch.max(outputs, 1)[1]
#             running_loss += loss.item() * batch_size
#             all_labels.extend(labels.to("cpu").detach().numpy().copy())
#             all_preds.extend(predicted.to("cpu").detach().numpy().copy())
#             dataset_size += batch_size
#             epoch_loss = running_loss / dataset_size


#         (acc, precision_macro, precision_micro, recall_macro, recall_micro, f1_macro, f1_micro,) = scores(all_labels, all_preds)
#         gc.collect()
#         return (
#             epoch_loss,
#             acc,
#             precision_macro,
#             precision_micro,
#             recall_macro,
#             recall_micro,
#             f1_macro,
#             f1_micro,
#         )

#     except Exception:
#         traceback.print_exc()



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
