# Manually finds the corresponiding 2D points
# Press q to quit, a to see the newest position clicked

import cv2,cv 
import numpy as np
corres_points = np.zeros([10,3])
mouseX,mouseY = -1,-1
i = 0

# mouse callback function
def draw_circle(event,x,y,flags,param):
	global mouseX,mouseY, i
	if event == cv2.EVENT_LBUTTONDOWN:
		cv2.circle(img1,(x,y),3,(0,255,0), thickness=1)
		cv2.imshow('image',img1)
		print 'Start Mouse Position: ' + str(x)+ ',' +str(y)
		corres_points[i,:] = [x,y,1]
		i += 1
# Create a black image, a window and bind the function to window
image1 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/tmp2.jpg'
image2 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/Test_x220_y66_z3_a5_t3.png'
img1 = cv2.imread(image1)
cv2.namedWindow('image')


img2 = cv2.imread(image2)
cv2.namedWindow('image2')
cv2.imshow('image2',img2)
cv2.setMouseCallback('image',draw_circle)
while True:
	cv2.imshow('image',img1)
	# User are allowed 5 mins to find correspondining points, after the time limit please exit the program and do it again
	k = cv2.waitKey(300000) & 0xFF
	if k == ord('q'):
		break
	elif k == ord('s'):
		cv2.imwrite('/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/tmp2_points.jpg',img1)

		np.save('tmp2',corres_points)
	cv2.destroyAllWindows()


