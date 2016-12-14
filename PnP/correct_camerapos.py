# This script is going to refine the camera poses from the neural network with the help of Perspektive-n-point algorithm (PnP)
# It takes three inarguments, the file with the camera matrix of the rendered image, 3D - 2D corresponding points
#The 2D points are honogenous and the two first elements are the camera pose used to render the image, which will be removed later
import numpy as np
import cv2,sys,math, time

def main(argv):
	print "start"
	camera_mtx = np.loadtxt(sys.argv[1], delimiter = " ")
	threeD_tmp = np.load(sys.argv[2]) 
	twoD_tmp = np.load(sys.argv[3]) #Homogenous

	distCoeffs = np.zeros((5,1)) #camera shouln't have any distortion
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
	n = 5
	#w = 0.5
	w_list = np.linspace(0.1,0.9,17)
	p = 0.8
	for w in w_list:
		print "now w is:", w
		k, sd = ransac_iterations(w,p,n)
		iteration = k + sd
		#print "w:",w
		#print "p:", p
		print "Iterations:", iteration
		#PnP Ransac
		start = time.clock()
		retval_ransac, rvec_ransac, tvec_ransac, inliers = cv2.solvePnPRansac(threeD_corres,twoD_corres, camera_mtx, dist_Coeffs, iterationsCount = iteration, reprojectionError = 3)
		end = time.clock()
		imgpts_ransac, jac_ransac = cv2.projectPoints(threeD_corres,rvec_ransac,tvec_ransac,camera_mtx,dist_Coeffs)

		# Calculate the mean projection error
		mean_error_ransac = mean_reprojection_error_all(imgpts_ransac,twoD_corres,threeD_corres)

		if inliers is not None:
			mean_reprojection_inliers = mean_reprojection_error_inliers(imgpts_ransac,twoD_corres,threeD_corres,inliers)
			print "Mean repoj error inliers:", mean_reprojection_inliers
			print "Numbers of inliners", len(inliers)
			percent_inliers = float(len(inliers))/len(twoD_corres)
			print "percent inliers:", percent_inliers
		else:
			print "No inlier exist"
		#print "Mean reprojection error:", mean_error

		#RANSAC Obtains the camera position 
		cam_pose_ransac, camera_pose_ransac, rotation_matrix_ransac, not_rodrigues = calc_camera_pose(rvec_ransac, tvec_ransac)

		euler_rotation = rotationMatrixToEulerAngles(rotation_matrix_ransac)

		print "cam_pose_ransac:"
		print cam_pose_ransac
		print "rotation matrix:"
		print rotation_matrix_ransac
		print "not rodrigues rotation matrix"
		print not_rodrigues
		print "time to do ransac:", end-start
		print "euler angles:", euler_rotation

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
	return cam_pose, camera_pose, rmatrix, np_rodrigues

# Calculates rotation matrix to euler angles The result is the same as MATLAB except the order of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(rotation):

	x = math.atan2(rotation[2,1] , rotation[2,2])
	y = math.atan2(-rotation[2,0], math.sqrt(rotation[2,1]*rotation[2,1] + rotation[2,2]*rotation[2,2]))
	z = math.atan2(rotation[1,0], rotation[0,0])

	return np.array([x, y, z])*180/math.pi

# calculates how many iterations is needed for RANSAC
def ransac_iterations(w, p, n):
	k = np.log(1 - p) / np.log(1 - w**n)
	sd = np.sqrt(1 - w**n)/(w**n)
	return int(np.ceil(k)), int(np.ceil(sd))

if __name__ == "__main__":
	main(sys.argv[1:])