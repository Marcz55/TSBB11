#This scrip is going to find the homogenous coordinates of the matching 2D corresponding points of two images.
# It takes two images as inargument and returns the coordinates of the matching points in respective image
import cv2, os, sys, re
import numpy as np
import pdb
from tempfile import TemporaryFile

# User input it text file with narrative camera parameters, location to queryImage and trainImage, primary camera pos from NN:
def main(argv):
	image1 = sys.argv[1]
	image2 = sys.argv[2]

	img1 = cv2.imread(image1,0)
	img2 = cv2.imread(image2,0)
	name1 = get_file_name(image1)
	name2 = get_file_name(image2)

	x_pos1, y_pos1, z_pos1, a_pos1, t_pos1 = get_render_camerapose(name1)
	x_pos2, y_pos2, z_pos2, a_pos2, t_pos2 = get_render_camerapose(name2)

	coord_img1, coord_img2 = corresponding_twoD_points(img1, img2)
	coord_img1[0,:] = [x_pos1, y_pos1,0]
	coord_img1[1,:] = [a_pos1, t_pos1,0]

	coord_img2[0,:] = [x_pos2, y_pos2,0]
	coord_img2[1,:] = [a_pos2, t_pos2,0]

	save_to_file(name1, coord_img1)
	save_to_file(name2, coord_img2)
	

# Takes two images, one rendered from the camera pose in the 3D model
# and the other one is the image taken with the camera, the two images has the same size
# returns the 2D corresponding points in each picture as an array
def corresponding_twoD_points(rendered_image, real_image):

	img1 = rendered_image
	img2 = real_image
	#camera_pos1 =
	#camera_pos2 = 
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
	return coord_img1, coord_img2

# Converts the matching points to homogenous (x,y) coordinated
# Returns homogenous 2D coordninates
def get_coordinates(matches, kp1, kp2):
	lenght_mat = len(matches)

	array_kp1 = np.empty([lenght_mat+2,3]) # Add 2 due to x,y,angle ,and tilt of camera
	array_kp2 = np.empty([lenght_mat+2,3])
	# Loop through all the matches
	i = 2
	for match in matches:

	# Get the matching keypoints for each of the images
		img1_idx = match.queryIdx
		img2_idx = match.trainIdx

	# x - columns
	# y - rows
	# Get the coordinates
		x1,y1 = kp1[img1_idx].pt
		x2,y2 = kp2[img2_idx].pt
	# Append to each list , homogenous coordiates
		array_kp1[i,:] = [x1,y1,1]
		array_kp2[i,:] = [x2,y2,1]
		i = i +1
	return array_kp1, array_kp2

# Save the correpsonding 2D points of each image to file with same name
def save_to_file(file_name, coordinates):
	np.save(file_name, coordinates)

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