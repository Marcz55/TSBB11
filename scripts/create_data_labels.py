from os import listdir
from os.path import isfile, join
import math
import argparse
import random

g_data_path = "/proj/camerapose/custom/data/working_dir/images/" # Change to directory of training/test images

# yaw: gaffla
# roll: phi
# pitch: theta
def euler_to_quat(yaw, roll, pitch):
    t0 = math.cos(yaw * 0.5)
    t1 = math.sin(yaw * 0.5)
    t2 = math.cos(roll * 0.5)
    t3 = math.sin(roll * 0.5)
    t4 = math.cos(pitch * 0.5)
    t5 = math.sin(pitch * 0.5)

#    return [(t0*t2*t4 + t1*t3*t5),
#            -(t0*t3*t4 - t1*t2*t5),
#            -(t0*t2*t5 + t1*t3*t4),
#            -(t1*t2*t4 - t0*t3*t5)]
    return [(t0*t2*t4 + t1*t3*t5),
            (t0*t3*t4 - t1*t2*t5),
            (t0*t2*t5 + t1*t3*t4),
            (t1*t2*t4 - t0*t3*t5)]

def quat_to_euler(quat):
#    ysqr = quat[2] * quat[2]
#    t0 = -2.0 * (ysqr + quat[3] * quat[3]) + 1.0;
#    t1 = +2.0 * (quat[1] * quat[2] - quat[0] * quat[3]);
#    t2 = -2.0 * (quat[1] * quat[3] + quat[0] * quat[2]);
#    t3 = +2.0 * (quat[2] * quat[3] - quat[0] * quat[1]);
#    t4 = -2.0 * (quat[1] * quat[1] + ysqr) + 1.0;
    ysqr = quat[2] * quat[2]
    t0 = 1.0 - 2.0 * (ysqr + quat[3] * quat[3]);
    t1 =  2.0 * (quat[1] * quat[2] + quat[0] * quat[3]);
    t2 =  2.0 * (quat[0] * quat[2] - quat[1] * quat[3]);
    t3 =  2.0 * (quat[0] * quat[1] + quat[2] * quat[3]);
    t4 = 1.0 - 2.0 * (quat[1] * quat[1] + ysqr);

    if(t2 > 1.0):
        t2 = 1.0
    elif(t2 < -1.0):
        t2 = -1.0

    yaw = math.atan2(t1,t0)
    roll = math.atan2(t3,t4)
    pitch = math.asin(t2)
    return([yaw, roll, pitch])

def cmp_float(x,y,eps):
    return abs(x-y) < eps

def create_dataset_txt(image_path, nof_train, nof_test):
    files = [f for f in listdir(image_path) if isfile(join(image_path,f))];
    ground_truth = []
    tmp = [0, 0]
    for f in files:
        f_notype = f.split('.')[0]
        given_tags = f_notype.split('_')

        yaw = float(given_tags[3][1:])*math.pi/180
        while(yaw > math.pi):
            yaw = yaw - 2*math.pi
        while(yaw < -math.pi):
            yaw = yaw + 2*math.pi
        roll = float(given_tags[4][1:])*math.pi/180
        while(roll > math.pi):
            roll = roll - 2*math.pi
        while(roll < -math.pi):
            roll = roll + 2*math.pi
        pitch = 0.0
        
        quat = euler_to_quat(yaw, roll, pitch)
        
        ground_truth.append([f,
                             '{0:.6f}'.format(float(given_tags[1][1:])),
                             '{0:.6f}'.format(float(given_tags[2][1:])),
                             '{0:.6f}'.format(1.0),
                             '{0:.6f}'.format(quat[0]),
                             '{0:.6f}'.format(quat[1]),
                             '{0:.6f}'.format(quat[2]),
                             '{0:.6f}'.format(quat[3])])

    if(len(ground_truth) < nof_train+nof_test):
        print("Error, found %d images, but %d + %d images requested. Exiting!"
              % (len(ground_truth), nof_train, nof_test))
        exit(0)
    
    random.shuffle(ground_truth)
    try:
        file_train = open(g_data_path + "../dataset_train.txt", 'w')
        file_test = open(g_data_path + "../dataset_test.txt", 'w')
        for i in range(0,nof_train):
            file_train.write("images/" + " ".join(ground_truth[i]) + "\n")
        for i in range(nof_train,nof_train+nof_test):
            file_test.write("images/" + " ".join(ground_truth[i]) + "\n")
    except Exception as e:
        print("Could not open a file to write")
        print(type(e))
        print("Exception string: " + str(e))
        exit(0)


#Visual Landmark Dataset V1
#ImageFile, Camera Position [X Y Z W P Q R]

parser = argparse.ArgumentParser(description="Creates the textfiles posenet uses as GT. This script assumes a lot about where the data should be obtained, see source.")
parser.add_argument("--nof_training_samples", type=int, required = True)
parser.add_argument("--nof_test_samples", type=int, required = True)
args = parser.parse_args()

create_dataset_txt(g_data_path, args.nof_training_samples, args.nof_test_samples)
