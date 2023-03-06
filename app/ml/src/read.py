import h5py

# categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
categories = ["athlete"]
is_debug = True
with h5py.File("../../../data/clean/athlete_debug/train.h5",'r') as f:
    print(f["label"])
    print(f["label"].keys())
    print(f["label/0"])
    print(f["label/0"][0])
    print(f["out_features"][0])