#This scrip is going to find the homogenous coordinates of the matching 2D corresponding points of two images.
# It takes two images as inargument and returns the coordinates of the matching points in respective image
import cv2, os, sys
import numpy as np
import pdb
from draw_matches import * 

# What do we need to do a PnP?
	# camera matrix : read in file with provided camera matrix 
	# 2D homogenous corresponding points (query image)
	# 3D homogenous corresponding points (rendered image)

# User input it text file with narrative camera parameters, location to queryImage and trainImage, primary camera pos from NN:
def main(argv):

	# uncomment these when the code are working, the user should give the script two images
	#img1 = sys.argv[1]
	#img2 = sys.argv[2]

	img1 = cv2.imread('TRtest_x24_y152_a308_t-3.png',0) # queryImage, grayscale
	img2 = cv2.imread('TRtest_x24_y160_a264_t-25.png',0) # trainImage, grayscale
	coord_img1, coord_img2 = corresponding_twoD_points(img1, img2)
	print coord_img2.shape

# Takes two images, one rendered from the camera pose in the 3D model
# and the other one is the image taken with the camera, the two images has the same size
# returns the 2D corresponding points in each picture as an array
def corresponding_twoD_points(rendered_image, real_image):

	img1 = rendered_image
	img2 = real_image
	# Create ORB detector with 1000 keypoints with a scaling pyramid factor
	# of 1.2
	orb = cv2.ORB(1000, 2)
	# Detect keypoints of original image
	(kp1,des1) = orb.detectAndCompute(img1, None)
	# Detect keypoints of rotated image
	(kp2,des2) = orb.detectAndCompute(img2, None)

	# Create matcher
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

	# Do matching
	matches = bf.match(des1,des2)

	# Sort the matches based on distance.  Least distance
	# is better
	matches = sorted(matches, key=lambda val: val.distance)

	# convert the matches to coordinates in image
	coord_img1, coord_img2 = get_coordinates(matches, kp1, kp2)
	#######
	surf = cv2.surf()
	key1,descr1 = surf.detectAndCompute(img1,None)
	key2,descr2 = surf.detectAndCompute(img2,None)

	# Show matches
	#drawMatches(img1, kp1, img2, kp2, matches[:20])
	return coord_img1, coord_img2

# Converts the matching points to homogenous (x,y) coordinated
# Returns homogenous 2D coordninates
def get_coordinates(matches, kp1, kp2):
	lenght_mat = len(matches)
	array_kp1 = np.empty([lenght_mat,3])
	array_kp2 = np.empty([lenght_mat,3])
	# Loop through all the matches
	i = 0
	for match in matches:

	# Get the matching keypoints for each of the images
		img1_idx = match.queryIdx
		img2_idx = match.trainIdx

	# x - columns
	# y - rows
	# Get the coordinates
		x1,y1 = kp1[img1_idx].pt
		x2,y2 = kp2[img2_idx].pt

	# Append to each list (homogenous coordinates)
		array_kp1[i,:] = [x1,y1,1]
		array_kp2[i,:] = [x2,y2,1]
		i = i +1
	return array_kp1, array_kp2


if __name__ == "__main__":
	main(sys.argv[1:])