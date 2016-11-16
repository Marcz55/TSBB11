# This script reads in a fodler with images and saves the SURF features for each image in a speparate file for each image.

import cv2
import numpy as np
import cPickle as pickle
from multiprocessing import Pool

# orh extraction
orb = cv2.orb()
path_to_folder = sys.argv[1]
path_save_folder= sys.argv[2]

def main():
	images = os.listdir(path_to_folder)
	pool = Pool()
	try:
		pool.map(find_keypoints, images)
		pool.close()
		pool.join()
	except:
		break:
	'''

	#Retrieve Keypoint Features
	keypoints_database = pickle.load( open( "keypoints_database.p", "rb" ) )
	kp1, desc1 = unpickle_keypoints(keypoints_database[0])
	kp1, desc1 = unpickle_keypoints(keypoints_database[1])
	'''

def find_keypoints(image):
	image_name = os.path.basename(image)
	file_name = path_save_folder + image_name + '.p'
	kp,des = orb.detectAndCompute(image,None)
	
	#Store and Retrieve keypoint features
	temp_array = []
	temp = pickle_keypoints(kp, des)
	temp_array.append(temp)
	pickle.dump(temp_array, open(file_name, "wb"))


def pickle_keypoints(keypoints, descriptors):
	i = 0
	temp_array = []
	for point in keypoints:
		temp = (point.pt, point.size, point.angle, point.response, point.octave,point.class_id, descriptors[i])
		++i
		temp_array.append(temp)
	return temp_array

def unpickle_keypoints(array):
	keypoints = []
	descriptors = []
	for point in array:
		temp_feature = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
		temp_descriptor = point[6]
		keypoints.append(temp_feature)
		descriptors.append(temp_descriptor)
	return keypoints, np.array(descriptors)


if __name__ == '__main__':
	main()