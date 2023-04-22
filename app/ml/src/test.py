import h5py
import cv2

data_dir="../../../data/origin/athlete"
with h5py.File(f"{data_dir}/train_batch.h5", "r") as f:
    for i in range(10):
        cv2.imwrite(f"img{i}.jpg", f["img"][i])
        
