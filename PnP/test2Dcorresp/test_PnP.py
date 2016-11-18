# Test PNP

import cv2
import numpy as np

objectPoints = np.random.random((10,3,1))

imagePoints = np.random.random((10,2,1))

cameraMatrix = np.eye(3)

distCoeffs = np.zeros((5,1))

retval, rvec, tvec = cv2.solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs)
print retval
print rvec
print tvec

