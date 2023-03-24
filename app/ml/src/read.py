import h5py
import matplotlib.pyplot as plt
import os
import cv2

# src_dir = f"../../../data/clean/athlete"
# path_h5 = {"train": f"{src_dir}/train.h5", "val": f"{src_dir}/val.h5", "test": f"{src_dir}/test.h5"}

# with h5py.File(path_h5["train"], "r") as f:
#     path = f["path"]
#     # print(path)
#     # print(path.keys())
#     img = f["img"]
#     id_wikidata = f["id_wikidata"]
#     label = f["label"]
#     for k in path.keys():
#         # print(path[k][0], img[k].shape, id_wikidata[k][0], label[k][0])
#         # print(type(path[k][0]), type(img[k][0]), type(id_wikidata[k][0]), type(label[k][0]))
#         filename = os.path.basename(path[k][0].decode())
#         # print(filename)
#         print(img[k][0].shape)
#         im = cv2.cvtColor(img[k][0], cv2.COLOR_BGR2RGB)
#         print(im.shape)
#         plt.imsave(f"{label[k]}_{filename}", im)

#     print(len(label))

data_dir = "../../../data/clean/aircraft"

path_h5 = {
    "train": f"{data_dir}/train.h5",
    "val": f"{data_dir}/val.h5",
    "test": f"{data_dir}/test.h5",
}

with h5py.File(path_h5["train"], "r") as f:
    # out_features = f["out_features"][0]
    print(f)
    print(f["out_features"])
    print(f["out_features"][0])