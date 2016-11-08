#Find features in the training data and saves them to file

import os, sys, cv2
import numpy as np
import cPickle


def main():

	#path_to_images = sys.argv[1]
	#file_name = sys.argv[2]

	#img1 = cv2.imread('../TRtest_x24_y152_a308_t-3.png',0) # queryImage
	#img2 = cv2.imread('../TRtest_x24_y160_a264_t-25.png',0) # trainImage
	surf = cv2.surf()
	tmp_array = []
	for image in os.listdir(path_to_images):
		if image.endswith(".png"):
			img = cv2.imread(image,0) # read in grayscale image
			kp, des = surf.detect(img, None, useProvidedKeypoints = False)
			temp = save_keypoints(kp,des)
			tmp_array.append(temp)
	cPickle.dump(temp_array, open(file_name, "wb"))
	file.close()



# save the keypoints and descriptors 
# returns an array with different parts of the keypoints and descriptors 
def save_keypoints(keypoints, descriptors):
	i = 0
	tmp_array = []

	for pnt in keypoints:
		tmp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id, descriptors[i])
		i += 1
		tmp_array.append(tmp)
		return temp_array

#Takes 
# returns the keypoints and descriptors for all images
def extract_keypoints_from_file(array):
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
        temp_descriptor = point[6]
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)


if __name__ == '__main__':
	main(argv[1:])