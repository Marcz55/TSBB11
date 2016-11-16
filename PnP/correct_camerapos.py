# This script is going to refine the camera poses from the neural network with the help of Perspektive-n-point algorithm (PnP)
# It takes three inarguments, the file with the camera matrix, path to two images, one rendered from the 3D image and one query image taken with the camera and finds the correpsonding 2D and 3D points in the images and performs PnP.

# What do we need to do a PnP?
	# camera matrix : read in file with provided camera matrix 
	# 2D homogenous corresponding points (query image)
	# 3D homogenous corresponding points (rendered image)
import numpy as np
import cv2,sys

def main(argv):

	camera_mtx = np.loadtxt(sys.argv[1], delimiter = " ")
	threeD_corres = np.load(sys.argv[2]) # Nonhomogenous
	twoD_corres = np.load(sys.argv[3])
	distCoeffs = np.zeros((5,1))

	tmp_array = np.zeros((587,2))
	for i in range(0,586):
		for j in range(0,2):
			tmp_array[i][j] = twoD_corres[i][j]

	twoD_corres = tmp_array

	# reshape to the correct size that PnP wants
	threeD_corres_reshape = np.reshape(threeD_corres, (-1,3,1))
	twoD_corres_reshape = np.reshape(twoD_corres, (-1,2,1))
	twoD_corres_reshape.astype(float)

	distCoeffs = np.zeros((5,1))

	retval, rvec, tvec = cv2.solvePnP(threeD_corres
	, twoD_corres, camera_mtx, distCoeffs)

	'''
	# Use Ransac to get a finer estimation, does not take homogenous coordinates
	rvec_ransac, tvec_ransac, inliers_ransac = cv2.SOLVEPNP_P3P(threeD_corres, twoD_corres, camera_mtx, 0, rvec_corse, tvec_corse, SOLVEPNP_ITERATIVE, iteration)
	'''

	# Obtains the camera position 
	R_transpose = rvec.transpose()
	camera_pos = -rvec*tvec
	print camera_pos


# Convert from homogenous points to euclidian points
def conv_to_euclid_coord(points, dim):
	size = points.shape
	if not dim == size[1]:
		coord = points[:,0:size[1]-1]
	else:
		coord = points
	return coord

if __name__ == "__main__":
	main(sys.argv[1:])