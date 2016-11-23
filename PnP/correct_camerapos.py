# This script is going to refine the camera poses from the neural network with the help of Perspektive-n-point algorithm (PnP)
# It takes three inarguments, the file with the camera matrix of the rendered image, 3D - 2D corresponding points
#The 2D points are honogenous and the two first elements are the camera pose used to render the image, which will be removed later
import numpy as np
import cv2,sys,math, time

def main(argv):
	camera_mtx = np.loadtxt(sys.argv[1], delimiter = " ")
	threeD_tmp = np.load(sys.argv[2]) #Homogenous
	twoD_tmp = np.load(sys.argv[3])

	distCoeffs = np.zeros((5,1)) # Blenders default camera shouln't have any distortion
	twoD_tmp = twoD_tmp[2:,:]
	len_twoD = len(twoD_tmp)
	len_threeD = len(threeD_tmp)

	if len_threeD != len_twoD:
		print "lenght of 3D corresp:" + str(len_threeD)
		print "lenght of 2D corresp:" + str(len_twoD)
		sys.exit("The lenght of the correspoing arrays do not match, program will exit")

	#Copys the two arrays to a new numpy array to be sure that the format is correct
	twoD_corres = copy_array(twoD_tmp,len_twoD,2)
	threeD_corres = copy_array(threeD_tmp,len_threeD,3)
	dist_Coeffs = np.zeros((5,1))

	# Initital solution from SolvePnP
	retval, rvecs, tvecs = cv2.solvePnP(threeD_corres, twoD_corres, camera_mtx, dist_Coeffs)
	# project 3D points to image plane
	imgpts, jac = cv2.projectPoints(threeD_corres, rvecs, tvecs, camera_mtx, dist_Coeffs)

	#Refined solution from ransac
	start = time.clock()
	rvec_ransac, tvec_ransac, inliers = cv2.solvePnPRansac(threeD_corres,twoD_corres, camera_mtx, dist_Coeffs,rvecs, tvecs,1, 10000,4)
	end = time.clock()
	imgpts_ransac, jac_ransac = cv2.projectPoints(threeD_corres,rvec_ransac,tvec_ransac,camera_mtx,dist_Coeffs)

	# Calculate the mean projection error
	mean_error = mean_reprojection_error_all(imgpts,twoD_corres,threeD_corres)
	mean_error_ransac = mean_reprojection_error_all(imgpts_ransac,twoD_corres,threeD_corres)

	if inliers is not None:
		mean_reprojection_inliers = mean_reprojection_error_inliers(imgpts_ransac,twoD_corres,threeD_corres,inliers)
		print "Mean repoj error inliers:", mean_reprojection_inliers
		print "Numbers of inliners", len(inliers)
	else:
		print "No inlier exist"
	#print "Mean reprojection error:", mean_error

	#RANSAC Obtains the camera position 
	cam_pose_ransac, camera_pose_ransac, rotation_matrix_ransac = calc_camera_pose(rvec_ransac, tvec_ransac)

	print "cam_pose_ransac:", cam_pose_ransac
	print "camera_pose_ransac:", camera_pose_ransac
	print "time to do ransac:", end-start

# copy the loaded npy array to a new npy array
def copy_array(array, len_of_array, dim):
	tmp_array = np.zeros((len_of_array,dim))
	for i in range(0,len_of_array):
		for j in range(0,dim):
			tmp_array[i][j] = array[i][j]
	return tmp_array

#Compute mean of reprojection error
def mean_reprojection_error_all(repojection_points, ground_truth,corresp_3D):
	tot_error=0
	total_points=0
	for i in range(0,len(repojection_points)):
		tot_error+=np.sum(np.abs(ground_truth[i]-repojection_points[i])**2)
		total_points+=len(corresp_3D[i])
	mean_error=np.sqrt(tot_error/total_points)
	return mean_error

#Compute mean of reprojection error
def mean_reprojection_error_inliers(repojection_points, ground_truth,corresp_3D,indices):
	tot_error=0
	total_points=0
	for e in indices:
		tot_error+=np.sum(np.abs(ground_truth[e]-repojection_points[e])**2)
		total_points+=len(corresp_3D[e])
	mean_error=np.sqrt(tot_error/total_points)
	return mean_error

#calculate the camera pose, two ways
def calc_camera_pose(rvec, tvec):
	np_rodrigues = np.asarray(rvec[:,:],np.float64)
	rmatrix = cv2.Rodrigues(np_rodrigues)[0]
	cam_pose = -np.matrix(rmatrix).T * np.matrix(tvec)
	camera_pose = -rmatrix.dot(tvec)
	return cam_pose, camera_pose, rmatrix

if __name__ == "__main__":
	main(sys.argv[1:])