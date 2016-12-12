#This scrip is going to find the homogenous coordinates of the matching 2D corresponding points of two images.
# It takes two images as inargument and returns the coordinates of the matching points in respective image
import cv2, os, sys, re, pdb
import numpy as np
from tempfile import TemporaryFile
from draw_matches import * 
from resizeimage import resizeimage
from matplotlib import pyplot as plt

# location to queryImage and trainImage, primary camera pos from NN:
def main(argv):
	image1 = sys.argv[1] # real
	image2 = sys.argv[2] # rendered
	#image1 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/20161003_111538_00009.31.18_small.jpg'
	#image2 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/Test_x220_y66_z3_a5_t3.png'
	img1 = cv2.imread(image1,0)
	img2 = cv2.imread(image2,0)
	name1 = get_file_name(image1)
	name2 = get_file_name(image2)

	x_pos2, y_pos2, z_pos2, a_pos2, t_pos2 = get_render_camerapose(name2)

	coord_img1, coord_img2 = corresponding_twoD_points(img1, img2)

	coord_img2[0,:] = [x_pos2, y_pos2, z_pos2]
	coord_img2[1,:] = [a_pos2, t_pos2,0]

	save_to_file(name1, coord_img1)
	save_to_file(name2, coord_img2)

# Takes two images, one rendered from the camera pose in the 3D model
# and the other one is the image taken with the camera, the two images has the same size
# returns the 2D corresponding points in each picture as an array
def corresponding_twoD_points(rendered_image, real_image):
	img1 = rendered_image
	img2 = real_image

	# Initiate SIFT detector
	sift = cv2.xfeatures2d.SIFT_create()

	# find the keypoints and descriptors with SIFT
	kp1, des1 = sift.detectAndCompute(img1,None)
	kp2, des2 = sift.detectAndCompute(img2,None)

	# FLANN parameters
	FLANN_INDEX_KDTREE = 1i
	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks=100)   # or pass empty dictionary

	flann = cv2.FlannBasedMatcher(index_params,search_params)

	matches = flann.knnMatch(des1,des2,k = 3)
	# convert the matches to coordinates in image
	query_Idx, train_Idx = get_matching_index(matches)
	coord_img1, coord_img2 = get_coordinates(kp1,kp2,query_Idx,train_Idx)
	return coord_img1, coord_img2

# Append all the matches to two lists
# returns two lists with indices
def get_matching_index(matches):
	train_Idx = []
	query_Idx = []
	for match in matches:
		#for i in range(0,len(match)):
		i = 0
		train = match[i].trainIdx
		query = match[i].queryIdx
		query_Idx.append(query)
		train_Idx.append(train)	
	return query_Idx, train_Idx

# Gets the coordinates for the matchings points in each image
# returns two arrays with coordinates
def get_coordinates(kp1, kp2, img1_idx, img2_idx):
	lenght_mat = len(img1_idx)

	array_kp1 = np.empty([lenght_mat+2,3]) # Add 2 due to x,y,z, angle ,and tilt of camera
	array_kp2 = np.empty([lenght_mat+2,3])
	# Loop through all the matches
	e = 2
	for i in range(0,lenght_mat):
		x1,y1 = kp1[img1_idx[i]].pt
		x2,y2 = kp2[img2_idx[i]].pt

		# Append to each list , homogenous coordiates
		array_kp1[e,:] = [x1,y1,1]
		array_kp2[e,:] = [x2,y2,1]
		e += 1
	return array_kp1, array_kp2
# Save the correpsonding 2D points of each image to file with same name as .npy files
def save_to_file(file_name, coordinates):
	np.save(file_name, coordinates)

# Finds the name of the image
def get_file_name(image):
	whole_name = os.path.basename(image)
	name, ext = os.path.splitext(whole_name)
	return name

# Get the camera pose which the image is rendered with
def get_render_camerapose(name):
	x = re.compile('(?<=_x)(.*?)(?=_y)')
	x_pos = x.findall(name)[0].replace('_','.')
	x_pos = float(x_pos)

	y = re.compile('(?<=_y)(.*?)(?=_z)')
	y_pos = y.findall(name)[0].replace('_','.')
	y_pos = float(y_pos)

	z = re.compile('(?<=_z)(.*?)(?=_a)')
	z_pos = z.findall(name)[0].replace('_','.')
	z_pos = float(z_pos)

	a = re.compile('(?<=_a)(.*?)(?=_t)')
	a_pos = a.findall(name)[0].replace('_','.')
	a_pos = float(a_pos)

	t = re.compile('(?<=_t).*$')
	t_pos = t.findall(name)[0].replace('_','.')
	t_pos = float(t_pos)

	return x_pos, y_pos, z_pos, a_pos, t_pos

if __name__ == "__main__":
	main(sys.argv[1:])