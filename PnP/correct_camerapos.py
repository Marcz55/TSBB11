# This script is going to refine the camera poses from the neural network with the help of Perspektive-n-point algorithm (PnP)
# It takes three inarguments, the file with the camera matrix of the rendered image, path to two images, one rendered from the 3D image and one query image taken with the camera and finds the correpsonding 2D and 3D points in the images and performs PnP.
import numpy as np
import cv2,sys,math

def main(argv):
	camera_mtx = np.loadtxt(sys.argv[1], delimiter = " ")
	threeD_tmp = np.load(sys.argv[2]) # Nonhomogenous
	twoD_tmp = np.load(sys.argv[3])
	distCoeffs = np.zeros((5,1))
	twoD_tmp = twoD_tmp[2:,:]
	len_twoD = len(twoD_tmp)
	len_threeD = len(threeD_tmp)

	if len_threeD != len_twoD:
		print "lenght of 3D corresp:" + str(len_threeD)
		print "lenght of 2D corresp:" + str(len_twoD)
		sys.exit("The lenght of the correspoing arrays do not match, program will exit")

	twoD_corres = copy_array(twoD_tmp,len_twoD,2)
	threeD_corres = copy_array(threeD_tmp,len_threeD,3)

	dist_Coeffs = np.zeros((5,1))

	retval, rvecs, tvecs = cv2.solvePnP(threeD_corres, twoD_corres, camera_mtx, dist_Coeffs)

	# project 3D points to image plane
	imgpts, jac = cv2.projectPoints(threeD_corres, rvecs, tvecs, camera_mtx, dist_Coeffs)

	rvec_ransac, tvec_ransac, inliners = cv2.solvePnPRansac(threeD_corres,twoD_corres, camera_mtx, dist_Coeffs) 

	imgpts_ransac, jac_ransac = cv2.projectPoints(threeD_corres,rvec_ransac,tvec_ransac,camera_mtx,dist_Coeffs)

	threeD_corres_reshape = np.reshape(threeD_corres, (-1,3,1))
	twoD_corres_reshape = np.reshape(twoD_corres, (-1,2,1))

	# Calculate the mean projection error
	mean_error = mean_reprojection_error(imgpts,twoD_corres,threeD_corres)
	mean_error_ransac = mean_reprojection_error(imgpts_ransac,twoD_corres,threeD_corres)
	#print "Mean reprojection error:", mean_error
	#print "Mean reprojection error RANSAC:", mean_error_ransac

	# Obtains the camera position 
	#rotvec = cv2.Rodrigues(rvecs)
	np_rodrigues = np.asarray(rvecs[:,:],np.float64)
	rmatrix = cv2.Rodrigues(np_rodrigues)[0]
	cam_pos = -np.matrix(rmatrix).T * np.matrix(tvecs)
	camera_pose = -rmatrix.dot(tvecs)
	print "camerapose1:", camera_pose
	print  "camerapose2:", cam_pos

def copy_array(array, len_of_array, dim):
	tmp_array = np.zeros((len_of_array,dim))
	for i in range(0,len_of_array):
		for j in range(0,dim):
			tmp_array[i][j] = array[i][j]
	return tmp_array

#Compute mean of reprojection error
def mean_reprojection_error(repojection_points, ground_truth,corresp_3D):
	tot_error=0
	total_points=0
	for i in range(0,len(repojection_points)):
		tot_error+=np.sum(np.abs(ground_truth[i]-repojection_points[i])**2)
		total_points+=len(corresp_3D[i])
	mean_error=np.sqrt(tot_error/total_points)


	return mean_error
if __name__ == "__main__":
	main(sys.argv[1:])