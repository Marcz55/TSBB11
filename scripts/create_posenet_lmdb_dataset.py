caffe_root = '/proj/camerapose/posenet/caffe-posenet/'  # Change to your directory to caffe-posenet
import sys
sys.path.insert(0, caffe_root + 'python')

import numpy as np
import lmdb
import cv2
import caffe
import random

random.seed()

directory = '/proj/camerapose/custom/data/working_dir/' # Change to your working directory
dataset0 = 'dataset_train.txt'
dataset1 = 'dataset_test.txt'
db0 = 'dataset_train_lmdb'
db1 = 'dataset_test_lmdb'

def main(dataset, db):

    poses = []
    images = []

    with open(directory+dataset) as f:
    #next(f)  # skip the 3 header lines
    #next(f)
    #next(f)
        for line in f:
            fname, p0,p1,p2,p3,p4,p5,p6 = line.split()
            p0 = float(p0)
            p1 = float(p1)
            p2 = float(p2)
            p3 = float(p3)
            p4 = float(p4)
            p5 = float(p5)
            p6 = float(p6)
            poses.append((p0,p1,p2,p3,p4,p5,p6))
            images.append(directory+fname)

    r = list(range(len(images)))
    random.shuffle(r)

    print('Creating PoseNet Dataset.')
    env = lmdb.open(directory+db, map_size=int(1e12))
    print('Opened database')

    count = 0

    for i in r:
        if count % 100 == 0:
            print('Saving image: '+str(count))#%d, (%d if counting only input images)', (count, count/8))
        X = cv2.imread(images[i])
        X = cv2.resize(X, (455,256))    # to reproduce PoseNet results, please resize the images so that the shortest side is 256 pixels
        for j in range(0, 1):
#            X2 = X*random.gauss(1.0, 0.2) + random.gauss(0.0, 48.0)
            X2 = X*random.gauss(1.0, 0.1) + random.gauss(0.0, 10.0)
            X2 = np.transpose(X2,(2,0,1))
            im_dat = caffe.io.array_to_datum(np.array(X2).astype(np.uint8))
            im_dat.float_data.extend(poses[i])
            str_id = '{:0>10d}'.format(count)
            with env.begin(write=True) as txn:
                txn.put(str_id, im_dat.SerializeToString())
            count = count+1

    env.close()

main(dataset0, db0)
main(dataset1, db1)

