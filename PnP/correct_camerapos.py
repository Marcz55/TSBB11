# This script is going to refine the camera poses from the neural network with the help of Perspektive-n-point algorithm (PnP)
# It takes three inarguments, the file with the camera matrix, path to two images, one rendered from the 3D image and one query image taken with the camera and finds the correpsonding 2D and 3D points in the images and performs PnP.

# What do we need to do a PnP?
	# camera matrix : read in file with provided camera matrix 
	# 2D homogenous corresponding points (query image)
	# 3D homogenous corresponding points (rendered image)
import numpy as np
import cv2

def main(argv):

	txt_path = sys.argv[1]
	threeD_corres = sys.argv[2]
	twoD_corres = sys.argv[3]
	#iteration = sys.argv[4]
	iteration = 100
	#confidence = 
	twoD_corres = conv_to_euclid_coord(twoD_corres,2)
	threeD_corres = conv_to_euclid_coord(threeD_corres,3)

	#This camera matrix should be the camera matrix from the camera used to rendered images
	camera_mtx = camera_mtx_from_file(txt_path)

	# Returns a corse estimate of the camera pose, does not take homogenous coordinates
	retval_corse, rvec_corse, tvec_corse = cv2.solvePnP(threeD_corres, twoD_corres, camera_mtx, 0 , SOLVEPNP_P3P)

	# Use Ransac to get a finer estimation, does not take homogenous coordinates
	rvec_ransac, tvec_ransac, inliers_ransac = cv2.calibrateCamera(threeD_corres, twoD_corres, camera_mtx, 0, rvec_corse, tvec_corse, SOLVEPNP_ITERATIVE, iteration)
	# Obtains the camera position 
	R_transpose = rvec_ransac.transpose()
	camera_pos = -R_transpose*tvec_ransac

# this function takes a text file with camera matrix and returns the camera matrix as a numpy matrix
# Returns camera matrix
def camera_mtx_from_file(txt_path):
	file = open(txt_path,'r')
	tmp_list = []
	K = np.empty([3,3], dtype = float)
	i = 0
	for line in file:
		line = line.replace(';', '' )
		x,y,z =  (line.split(","))
		K[i][0] = float(x)
		K[i][1] = float(y)
		K[i][2] = float(z)
	return K

def conv_to_euclid_coord(points, dim):
	size = points.shape
	if not dim == size[1]:
		coord = points[:,0:size[1]-1]
	else:
		coord = points
	return coord



if __name__ == "__main__":
	main(sys.argv[1:])