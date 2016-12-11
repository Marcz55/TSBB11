#!/bin/bash

python /proj/camerapose/custom/scripts/create_posenet_lmdb_dataset.py
/proj/camerapose/posenet/caffe-posenet/build/tools/compute_image_mean /proj/camerapose/custom/data/working_dir/dataset_train_lmdb /proj/camerapose/custom/data/working_dir/imagemean.binaryproto
