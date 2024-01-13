import sys, os, gc, copy, time, datetime, json

from collections import defaultdict
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from omegaconf import OmegaConf
import hydra
import h5py
import warnings
from colorama import Fore, Style
import wandb
import logging
import logging.config
from yaml import safe_load

sys.path.append(os.path.join(os.path.dirname(__file__), "entity_linking/yolov5"))
from entity_linking.util import *
from entity_linking.data import *
from entity_linking.model import *
from entity_linking.train import *

b_ = Fore.BLUE
sr_ = Style.RESET_ALL

warnings.filterwarnings("ignore")
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

wandb.login()

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

# TODO: 
# - after testing using aircraft, confirm to tpo-k entities
# - if it is ok, VQA using predicted top-k entities
# - when using gpt-3.5, there is necessity to split sentneces because of limitation of tokens
# python 4_ml.py data.category=aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-4


def run_training(dataloaders, model, optimizer, scheduler, device, cfg, run, save_dir):
    logger.info(f"scheduler: {scheduler}")
    logger.info(f"optimizer: {optimizer}")

    # To log gradients automatically
    wandb.watch(model, log_freq=100)

    if torch.cuda.is_available():
        print("[INFO] Using GPU: {}\n".format(torch.cuda.get_device_name()))

    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"save_dir: {save_dir}")

    start = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_epoch_loss = np.inf
    history = defaultdict(list)
    for epoch in range(1, cfg.train.epochs + 1):
        gc.collect()
        logger.info(f"epoch: {epoch}/{cfg.train.epochs}")

        logger.info("train step")
        (train_loss, train_acc, train_precision_macro, train_precision_micro, train_recall_macro, train_recall_micro, train_f1_macro, train_f1_micro,) = train_one_epoch(
            dataloaders["train"], model, criterion, optimizer, scheduler, device, n_accumulate=cfg.train.n_accumulate, enable_amp_half_precision=cfg.train.enable_amp_half_precision,
        )

        logger.info("valid step")
        (val_loss, val_acc, val_precision_macro, val_precision_micro, val_recall_macro, val_recall_micro, val_f1_macro, val_f1_micro, val_top1_accuracy, val_top2_accuracy, val_top3_accuracy, val_top5_accuracy, val_top10_accuracy, val_top20_accuracy, id_indices_confidences_dict,) = valid_one_epoch(dataloaders["val"], model, criterion, device, top_k=cfg.train.top_k)

        history = {
            "Epoch": epoch,
            "LR": optimizer.param_groups[0]["lr"],
            "Train Loss": train_loss,
            "Train Acc": train_acc,
            "Train Macro Precision": train_precision_macro,
            "Train Micro Precision": train_precision_micro,
            "Train Macro Recall": train_recall_macro,
            "Train Micro Recall": train_recall_micro,
            "Train Macro F1": train_f1_macro,
            "Train Micro F1": train_f1_micro,
            "Valid Loss": val_loss,
            "Valid Acc": val_acc,
            "Valid Macro Precision": val_precision_macro,
            "Valid Micro Precision": val_precision_micro,
            "Valid Macro Recall": val_recall_macro,
            "Valid Micro Recall": val_recall_micro,
            "Valid Macro F1": val_f1_macro,
            "Valid Micro F1": val_f1_micro,
            "Top-01 Accuracy": val_top1_accuracy,
            "Top-02 Accuracy": val_top2_accuracy,
            "Top-03 Accuracy": val_top3_accuracy,
            "Top-05 Accuracy": val_top5_accuracy,
            "Top-10 Accuracy": val_top10_accuracy,
            "Top-20 Accuracy": val_top20_accuracy,
        }

        # Convert indices and confidences to Python lists for JSON serialization
        # indices_list = all_indices.tolist()
        # confidences_list = all_confidences.tolist()

        # Save indices and confidences to a JSON file
        # indices_confidences_file = f"{save_dir}/indices_confidences_epoch{epoch}.json"
        # with open(indices_confidences_file, "w") as file:
        #     json.dump({"indices": all_indices, "confidences": all_confidences}, file)

        # 辞書型として、予測対象のidをkey, 予測したtop-kのidsとそれぞれのconfidenceをvalueとして保存する
        # Save indices and confidences to a JSON file
        indices_confidences_file = f"{save_dir}/id_indices_confidences_epoch{epoch}.json"
        with open(indices_confidences_file, "w") as file:
            json.dump(id_indices_confidences_dict, file)

        # Log additional values for each step
        # wandb.log({"Top-K Accuracy": val_topk_accuracy}, step=epoch)

        wandb.log(history, step=epoch)

        # Save model weight
        if val_loss <= best_epoch_loss:
            print(f"{b_}Validation Loss Improved ({best_epoch_loss} ---> {val_loss})")
            best_epoch_loss = val_loss
            run.summary["Best Loss"] = best_epoch_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            PATH = f"{save_dir}/Loss{best_epoch_loss:.4f}_epoch{epoch:.0f}.bin"
            torch.save(model.state_dict(), PATH)
            # Save a model file from the current directory
            print(f"Model Saved{sr_}")
        print()

    end = time.time()
    time_elapsed = end - start
    logger.info("Training complete in {:.0f}h {:.0f}m {:.0f}s".format(time_elapsed // 3600, (time_elapsed % 3600) // 60, (time_elapsed % 3600) % 60,))
    logger.info("Best Loss: {:.4f}".format(best_epoch_loss))
    model.load_state_dict(best_model_wts)
    return model, history


# python 4_ml.py data.category=aircraft data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=1e-4
# def run_training(dataloaders, model, optimizer, scheduler, device, cfg, run, save_dir):
#     logger.info(f"scheduler: {scheduler}")
#     logger.info(f"optimizer: {optimizer}")

#     # To log gradients automatically
#     wandb.watch(model, log_freq=100)

#     if torch.cuda.is_available():
#         print("[INFO] Using GPU: {}\n".format(torch.cuda.get_device_name()))

#     os.makedirs(save_dir, exist_ok=True)
#     logger.info(f"save_dir: {save_dir}")

#     start = time.time()
#     best_model_wts = copy.deepcopy(model.state_dict())
#     best_epoch_loss = np.inf
#     history = defaultdict(list)
#     for epoch in range(1, cfg.train.epochs + 1):
#         gc.collect()
#         logger.info(f"epoch: {epoch}/{cfg.train.epochs}")

#         logger.info("train step")
#         (train_loss, train_acc, train_precision_macro, train_precision_micro, train_recall_macro, train_recall_micro, train_f1_macro, train_f1_micro,) = train_one_epoch(
#             dataloaders["train"], model, criterion, optimizer, scheduler, device, n_accumulate=cfg.train.n_accumulate, enable_amp_half_precision=cfg.train.enable_amp_half_precision,
#         )

#         logger.info("valid step")
#         (val_loss, val_acc, val_precision_macro, val_precision_micro, val_recall_macro, val_recall_micro, val_f1_macro, val_f1_micro,) = valid_one_epoch(dataloaders["val"], model, criterion, device)

#         history = {
#             "Epoch": epoch,
#             "LR": optimizer.param_groups[0]["lr"],
#             "Train Loss": train_loss,
#             "Train Acc": train_acc,
#             "Train Macro Precision": train_precision_macro,
#             "Train Micro Precision": train_precision_micro,
#             "Train Macro Recall": train_recall_macro,
#             "Train Micro Recall": train_recall_micro,
#             "Train Macro F1": train_f1_macro,
#             "Train Micro F1": train_f1_micro,
#             "Valid Loss": val_loss,
#             "Valid Acc": val_acc,
#             "Valid Macro Precision": val_precision_macro,
#             "Valid Micro Precision": val_precision_micro,
#             "Valid Macro Recall": val_recall_macro,
#             "Valid Micro Recall": val_recall_micro,
#             "Valid Macro F1": val_f1_macro,
#             "Valid Micro F1": val_f1_micro,
#         }
#         wandb.log(history, step=epoch)

#         # Save model weight
#         if val_loss <= best_epoch_loss:
#             print(f"{b_}Validation Loss Improved ({best_epoch_loss} ---> {val_loss})")
#             best_epoch_loss = val_loss
#             run.summary["Best Loss"] = best_epoch_loss
#             best_model_wts = copy.deepcopy(model.state_dict())
#             PATH = f"{save_dir}/Loss{best_epoch_loss:.4f}_epoch{epoch:.0f}.bin"
#             torch.save(model.state_dict(), PATH)
#             # Save a model file from the current directory
#             print(f"Model Saved{sr_}")
#         print()

#     end = time.time()
#     time_elapsed = end - start
#     logger.info("Training complete in {:.0f}h {:.0f}m {:.0f}s".format(time_elapsed // 3600, (time_elapsed % 3600) // 60, (time_elapsed % 3600) % 60,))
#     logger.info("Best Loss: {:.4f}".format(best_epoch_loss))
#     model.load_state_dict(best_model_wts)
#     return model, history


def criterion(outputs, labels):
    return nn.CrossEntropyLoss()(outputs, labels)


# Change
# weight_dir
# 画像認識器の訓練、テストの実行
# 注意: 画像枚数がbatch_sizeに満たない場合は、エラーが出る。その場合はbatch_sizeを小さくするか、画像枚数を増やすかする必要がある。
# TODO: TOP-Kの予測結果が出力されるように変更する。これをやる。
@hydra.main(config_path="../conf/", config_name="config.yml")
def main(cfg: OmegaConf):
    logger.info(f"cfg.data.category: {cfg.data.category}")
    logger.info(f"cfg.data.batch_size.train: {cfg.data.batch_size.train}")
    logger.info(f"cfg.data.batch_size.val: {cfg.data.batch_size.val}")

    # Seed
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    set_seed(cfg.general.seed)

    # Dataset
    path_h5 = {
        "train": f"{cfg.data.data_dir}/train.h5",
        # "val": f"{cfg.data.data_dir}/val.h5",
        "val": f"{cfg.data.data_dir}/test.h5",
        # "test": f"{cfg.data.data_dir}/test.h5",
    }
    data_transforms = GetTransforms(cfg.data.img_size)
    dataloaders = prepare_loaders(path_h5, data_transforms, cfg.data.batch_size, is_train=cfg.general.is_train, fold=0,)

    with h5py.File(path_h5["train"], "r") as f:
        out_features = f["out_features"][0]
    logger.info(f"out_features = {out_features}")
    model = EntityLinkingModel(cfg.model.model_name, out_features)
    model.to(device)
    weight_dir = f"../weights/clean/{cfg.data.category}"

    if cfg.general.is_train:
        optimizer = optim.Adam(model.parameters(), lr=cfg.optimizer.learning_rate, weight_decay=cfg.optimizer.weight_decay,)
        scheduler = fetch_scheduler(optimizer, cfg.optimizer.scheduler, cfg.optimizer.T_max, cfg.optimizer.learning_rate * 0.1,)

        dt_now = datetime.datetime.now()
        now = f"{str(dt_now.month).zfill(2)}{str(dt_now.day).zfill(2)}-{str(dt_now.hour).zfill(2)}{str(dt_now.minute).zfill(2)}{str(dt_now.second).zfill(2)}"
        save_dir = f"{weight_dir}/{now}"

        run = wandb.init(project="VEL", name=f"{cfg.data.category}_{now}", config=OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True),)
        model, history = run_training(dataloaders, model, optimizer, scheduler, device, cfg, run, save_dir)
        run.finish()
    else:
        model.load_state_dict(torch.load(f"{weight_dir}/{cfg.model.weight_file}"))
        model.eval()
        logger.info("test step")
        (val_loss, val_acc, val_precision_macro, val_precision_micro, val_recall_macro, val_recall_micro, val_f1_macro, val_f1_micro,) = valid_one_epoch(dataloaders, model, criterion, device)
        l_names = [
            "Acc",
            "Loss",
            "Macro Precision",
            "Micro Precision",
            "Macro Recall",
            "Micro Recall",
            "Macro F1",
            "Micro F1",
        ]
        l_vals = [
            val_loss, 
            val_acc, 
            val_precision_macro, 
            val_precision_micro, 
            val_recall_macro, 
            val_recall_micro, 
            val_f1_macro, 
            val_f1_micro,
        ]
        for name, val in zip(l_names, l_vals):
            logger.info(f"{name}: {val}")
    # visualize_model(dataloaders, model, device)


if __name__ == "__main__":
    main()
