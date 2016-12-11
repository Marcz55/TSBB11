import cv2
import os
os.environ['GLOG_minloglevel'] = '2'
import caffe
os.environ['GLOG_minloglevel'] = '1'
import argparse
import numpy as np
import random
import math

def quat_to_euler(quat):
    ysqr = quat[2] * quat[2]
    t0 = -2.0 * (ysqr + quat[3] * quat[3]) + 1.0;
    t1 = +2.0 * (quat[1] * quat[2] - quat[0] * quat[3]);
    t2 = -2.0 * (quat[1] * quat[3] + quat[0] * quat[2]);
    t3 = +2.0 * (quat[2] * quat[3] - quat[0] * quat[1]);
    t4 = -2.0 * (quat[1] * quat[1] + ysqr) + 1.0;

    if(t2 > 1.0):
        t2 = 1.0
    elif(t2 < -1.0):
        t2 = -1.0

    yaw = math.atan2(t1,t0)
    roll = math.atan2(t3,t4)
    pitch = math.asin(t2)

    return([yaw, roll, pitch])

def normalize(quat):
    return quat/np.linalg.norm(quat)

def print_result(result):
    print(result)

    print('Average cls3_fc_wpqr: ', np.average(result['cls3_fc_wpqr'], axis=0))
    print('Average cls1_fc_xyz: ', np.average(result['cls1_fc_xyz'], axis=0))
    print('Average cls3_fc_xyz: ', np.average(result['cls3_fc_xyz'], axis=0))
    print('Average cls2_fc_wpqr: ', np.average(result['cls2_fc_wpqr'], axis=0))
    print('Average cls1_fc_wpqr: ', np.average(result['cls1_fc_wpqr'], axis=0))
    print('Average cls2_fc_xyz: ', np.average(result['cls2_fc_xyz'], axis=0))

    print('Angles [in_plane roll pitch]: ', quat_to_euler(normalize(np.average(result['cls1_fc_wpqr'], axis=0))))
    print('Angles [in_plane roll pitch]: ', quat_to_euler(normalize(np.average(result['cls2_fc_wpqr'], axis=0))))
    print('Angles [in_plane roll pitch]: ', quat_to_euler(normalize(np.average(result['cls3_fc_wpqr'], axis=0))))

def print_result_to_file(result, image_name):
    try:
        f = open('prediction_result.txt', 'a')
        #print('### SUCCHESS')
        pos = np.average(result['cls3_fc_xyz'], axis=0)
        angles = quat_to_euler(normalize(np.average(result['cls3_fc_wpqr'], axis=0)))
        lst = [' x:', str(pos[0]), ' y:', str(pos[1]), ' z:', str(pos[2]), ' angle:', str(180*angles[0]/3.14159265358979323)]
        print(image_name + " " + " ".join(lst)+"\n")
        f.write(image_name + "\n" + " ".join(lst)+"\n\n")
        f.close()
    except Exception as e:
        print("Could not open a file to write")
        print(type(e))
        print("Exception string: " + str(e))
        exit(0)

def predict_sample(image_path, mean_image, net):
    im_raw = np.moveaxis(cv2.resize(cv2.imread(image_path),(455,256)), -1, 0)

#    tmp = im_raw
#    im_raw[0,:,:] = tmp[2,:,:]
#    im_raw[2,:,:] = tmp[0,:,:]
    im = im_raw - mean_image
    
    batch = np.zeros((40,3,224,224))
    for i in range(0, 40):
        x = random.randint(0,455 - 224)
        y = random.randint(0,256 - 224)
        input_image = im[:, y:y+224, x:x+224]
        batch[i,:,:,:] = input_image

    result = net.forward_all(data = batch)
    return result

def get_mean_image(image_path, image_names):
    total_image = np.zeros(cv2.imread(image_path + "/" + image_names[0]).shape)
    for im_name in image_names:
        total_image = total_image + cv2.imread(image_path + "/" + im_name)
    return total_image / len(image_names)

def predict(model, image_mean, weights, image_path):
    caffe.set_mode_gpu();
    net = caffe.Net(model,
                    weights,
                    caffe.TEST)

    blob_meanfile = caffe.proto.caffe_pb2.BlobProto()
    data_meanfile = open(image_mean , 'rb' ).read()
    blob_meanfile.ParseFromString(data_meanfile)
    mean = np.squeeze(np.array( caffe.io.blobproto_to_array(blob_meanfile)))

    if(os.path.isdir(image_path)):
        image_names = os.listdir(image_path)
        image_names.sort()
        mean_input = np.moveaxis(get_mean_image(image_path, image_names), -1, 0)
        for im in image_names:
            print('Treating ' + im)
            result = predict_sample(image_path+"/"+im, mean, net)
#            result = predict_sample(image_path+"/"+im, mean, net)
            print_result_to_file(result, im)
    else:
        result = predict_sample(image_path, mean, net)
        print_result(result)

parser = argparse.ArgumentParser(description="Predicts the 6DOF camerapose from a given image. For instance:\n > python predict_sample.py --image_path data/my_fabulous_data/img00.png --deploy_prototxt scripts/models/train_bayesian_posenet.prototxt --image_mean data/my_fabulous_data/imagemean.binaryproto --trained_net new_snapshots/snapshots_iter_20000.caffemodel")
parser.add_argument("--image_path", type=str, required = True)
parser.add_argument("--deploy_prototxt", type=str, required = True)
parser.add_argument("--image_mean", type=str, required = True)
parser.add_argument("--trained_net", type=str, required = True)
args = parser.parse_args()

predict(args.deploy_prototxt, args.image_mean, args.trained_net, args.image_path)

