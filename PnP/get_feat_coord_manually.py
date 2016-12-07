# Manually finds the corresponiding 2D points
# Press q to quit, a to see the newest position clicked
# when 10 points is choosen on the first image, press on the second image, close it with either ctrl + w or cmd + w and start press on the correspondong points in the second image, in the right order. 

import cv2 , sys, os
import numpy as np
i = 0
corres_points = np.zeros([10,3])
corres_points2 = np.zeros([10,3])
mouseX,mouseY = -1,-1

image1 = sys.argv[1]
image2 = sys.argv[2]
#image1 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/20161003_111538_00009.31.18_small.jpg'
#image2 = '/Users/samanthavi/Documents/TSBB11/TSBB11---Camera-poses/PnP/Test_x220_y66_z3_a5_t3.png'

img1 = cv2.imread(image1)
img2 = cv2.imread(image2)
def main():
	cv2.namedWindow('image')
	cv2.namedWindow('image2')
	cv2.imshow('image2',img2)
	name1 = get_file_name(image1)
	name2 = get_file_name(image2)

	while True:
		if i <10:
			cv2.imshow('image',img1)
			cv2.setMouseCallback('image',draw_circle)
			# User are allowed 5 mins to find correspondining points
			k = cv2.waitKey(300000) & 0xFF
		if i>=10:
			cv2.namedWindow('image2')
			cv2.setMouseCallback('image2',draw_circle)
			# User are allowed 5 mins to find correspondining points
			k = cv2.waitKey(300000) & 0xFF
		if k == ord('q'):
			break

		elif k == ord('s'):
			cv2.imwrite(name1,img1)
			cv2.imwrite(name2,img2)
			np.save('tmp',corres_points)
			np.save('tmp2',corres_points2)
	cv2.destroyAllWindows()


# mouse callback function
def draw_circle(event,x,y,flags,param):
	global mouseX,mouseY, i
	if event == cv2.EVENT_LBUTTONDOWN:
		if i == 10:
			print "change image"
		if i < 10:
			cv2.circle(img1,(x,y),3,(0,255,0), thickness=1)
			cv2.imshow('image',img1)
			print 'Start Mouse Position: ' + str(x)+ ',' +str(y)
			corres_points[i,:] = [x,y,1]
			i += 1
		elif i >= 10:
			cv2.circle(img2,(x,y),3,(0,255,0), thickness=1)
			cv2.imshow('image2',img2)
			print 'Start Mouse Position2: ' + str(x)+ ',' + str(y)
			corres_points2[i-10,:] = [x,y,1]
			i += 1

# finds name of the image taken
def get_file_name(image):
	whole_name = os.path.basename(image)
	name, ext = os.path.splitext(whole_name)
	return name

if __name__ == '__main__':
	main(sys.argv[1:])
