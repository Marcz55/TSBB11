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

def apply_color_transform(im_raw, color_transform):
    # im_raw of shape (3, 256, 455)
#    import matplotlib.pyplot as plt

    # Make it RGB
    im_raw_rgb = np.zeros(im_raw.shape)
    im_raw_rgb[0,:,:] = im_raw[2,:,:]
    im_raw_rgb[1,:,:] = im_raw[1,:,:]
    im_raw_rgb[2,:,:] = im_raw[0,:,:]
#    plt.imshow(np.moveaxis(im_raw_rgb,0,-1))
#    plt.show()
#    print(color_transform)

    # Apply color transform pixel-wise
    im0 = im_raw_rgb.reshape((3,im_raw.shape[1]*im_raw.shape[2]))
    im1 = np.dot(color_transform, im0)
    im2 = im1.reshape((3,im_raw.shape[1],im_raw.shape[2]))
#    print(im2[:,10,150]/256)

#    plt.imshow(np.moveaxis(im2/256,0,-1))
#    plt.show()
    
    # Make it BGR again
    im3 = np.zeros(im2.shape)
    im3[0,:,:] = im2[2,:,:]
    im3[1,:,:] = im2[1,:,:]
    im3[2,:,:] = im2[0,:,:]
    return im3

def predict_sample(image_path, mean_image, net, color_transform):
    im_raw = np.moveaxis(cv2.imread(image_path), -1, 0)
    im_color_transformed = apply_color_transform(im_raw, color_transform)
    im = im_color_transformed - mean_image
    
    batch = np.zeros((40,3,224,224))
    for i in range(0, 40):
        x = random.randint(0,455 - 224)
        y = random.randint(0,256 - 224)
        input_image = im[:, y:y+224, x:x+224]
        batch[i,:,:,:] = input_image

    result = net.forward_all(data = batch)
    return result

def get_mean_image(image_path, image_names):
    tmp = ''
    for im_name in image_names:
        if(im_name.endswith('.jpg')):
            tmp = im_name
    total_image = np.zeros(cv2.imread(image_path + "/" + tmp).shape)
    for im_name in image_names:
        if(im_name.endswith('jpg')):
            total_image = total_image + cv2.imread(image_path + "/" + im_name)
    return total_image / len(image_names)

# Assumes presence of a gt.txt, with each nonempty line containing
# imagename x y z angle_in_plane
def read_gt_to_dictionary(image_path):
    f = open(image_path+'/gt.txt')
    gt = {}
    for line in f:
        tokens = line.rstrip('\n').split(' ')
        gt[tokens[0]] = [float(tokens[1]), float(tokens[2]), float(tokens[3]), float(tokens[4])]
#        while(gt[tokens[0]][-1] > 180):
#            gt[tokens[0]][-1] = gt[tokens[0]][-1] - 180
#        while(gt[tokens[0]][-1] < -180):
#            gt[tokens[0]][-1] = gt[tokens[0]][-1] + 180
    f.close()
    return gt

def get_my_error_string(left, right):
    dist_err = math.sqrt((left[0]-right[0])*(left[0]-right[0]) + 
                         (left[1]-right[1])*(left[1]-right[1]) + 
                         (left[2]-right[2])*(left[2]-right[2]))
    alpha = 3.14159265358979323/180 * left[3]
    beta = 3.14159265358979323/180 * right[3]
    angle_err = 180/3.14159265358979323*math.acos(math.cos(alpha)*math.cos(beta)+math.sin(alpha)*math.sin(beta))
    return str(dist_err) + ' ' + str(angle_err)

def read_mat_from_txt(path):
    f = open(path)
    # @todo should check f viability here
    mat = np.zeros((3,3))
    row = 0
    for line in f:
        tokens = line.rstrip('\n').split(' ')
        for col in range(0,len(tokens)):
            mat[row,col] = tokens[col]
        row = row + 1
    return mat

def test(model, image_mean, weights, image_path):
    caffe.set_mode_gpu();
    net = caffe.Net(model,
                    weights,
                    caffe.TEST)

    gt_dict = read_gt_to_dictionary(image_path)

    blob_meanfile = caffe.proto.caffe_pb2.BlobProto()
    data_meanfile = open(image_mean , 'rb' ).read()
    blob_meanfile.ParseFromString(data_meanfile)
    mean = np.squeeze(np.array( caffe.io.blobproto_to_array(blob_meanfile)))
    color_transform = read_mat_from_txt(image_path+"/color_transform.dat")

    if(os.path.isdir(image_path)):
        image_names = os.listdir(image_path)
        image_names.sort()
        mean_input = np.moveaxis(get_mean_image(image_path, image_names), -1, 0)
        for im in image_names:
            if(im.endswith('.jpg')):
                print('')
                print('Treating ' + im)
                result = predict_sample(image_path+"/"+im, mean, net, color_transform)
#                result = predict_sample(image_path+"/"+im, mean_input, net)
#                print(result)
#                print(result['cls3_fc_xyz'])
                prediction = np.average(result['cls3_fc_xyz'], axis=0)
                result_mod = [prediction[0], prediction[1], prediction[2], 
                              quat_to_euler(normalize(np.average(result['cls3_fc_wpqr'], 
                                                                 axis=0)))[0]*
                              180/3.1415926535]
                distance_me = np.average(np.sqrt(np.sum(np.square(
                                result['cls3_fc_xyz'] - prediction), axis = 1)), axis=0)
                print('pred: ' + str(result_mod))
                print(' gt : ' + str(gt_dict[im]))
                print('err : ' + get_my_error_string(result_mod, gt_dict[im]))
                print(' me : ' + str(distance_me))
#               print_result_to_file(result, im)

parser = argparse.ArgumentParser(description="Predicts the 6DOF camerapose for a directory of test images, comparing to a ground truth. For instance:\n > python predict_sample.py --image_path data/my_fabulous_data --deploy_prototxt scripts/models/train_bayesian_posenet.prototxt --image_mean data/my_fabulous_data/imagemean.binaryproto --trained_net new_snapshots/snapshots_iter_20000.caffemodel")
parser.add_argument("--image_path", type=str, required = True)
parser.add_argument("--deploy_prototxt", type=str, required = True)
parser.add_argument("--image_mean", type=str, required = True)
parser.add_argument("--trained_net", type=str, required = True)
args = parser.parse_args()

test(args.deploy_prototxt, args.image_mean, args.trained_net, args.image_path)

