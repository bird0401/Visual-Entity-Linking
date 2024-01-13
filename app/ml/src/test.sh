#!/bin/sh

# TODO: TOP-Kをいくつかに変えて実験を行う
command=(
"python ./4_ml.py data.category=aircraft data.data_dir=../../../data/aircraft data.batch_size.train=32 data.batch_size.val=32 optimizer.learning_rate=1e-4 train.top_k=5"
"python ./4_ml.py data.category=athlete data.data_dir=../../../data/athlete data.batch_size.train=4 data.batch_size.val=8 optimizer.learning_rate=1e-4 train.top_k=5"
"python ./4_ml.py data.category=bird data.data_dir=../../../data/bird data.batch_size.train=32 data.batch_size.val=32 optimizer.learning_rate=1e-3 train.top_k=5"
"python ./4_ml.py data.category=bread data.data_dir=../../../data/bread data.batch_size.train=32 data.batch_size.val=64 optimizer.learning_rate=5e-4 train.top_k=5"
"python ./4_ml.py data.category=car data.data_dir=../../../data/car data.batch_size.train=16 data.batch_size.val=32 optimizer.learning_rate=1e-4 train.top_k=5"
"python ./4_ml.py data.category=director data.data_dir=../../../data/director data.batch_size.train=64 data.batch_size.val=128 optimizer.learning_rate=1e-3 train.top_k=5"
"python ./4_ml.py data.category=dog data.data_dir=../../../data/dog data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 train.top_k=5"
"python ./4_ml.py data.category=us_politician data.data_dir=../../../data/us_politician data.batch_size.train=128 data.batch_size.val=256 optimizer.learning_rate=5e-4 train.top_k=5")

num_gpus=8

for i in $(seq 0 $((${num_gpus}-1))); do
    CUDA_VISIBLE_DEVICES=$i ${command[$i]} &
done

wait

