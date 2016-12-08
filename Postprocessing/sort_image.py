# This script sorts ways images with to much blue sky in it.
# The inparameters are the path to the folder with images and where the unwanted images shall be saved

import numpy as np
import cv2, shutil, sys, os
import time
from multiprocessing import Pool

path_to_folder = sys.argv[1]
dest_path = sys.argv[2]
thres_blue = 0.4
thres_green = 0.3
thres_both = 0.6
height = 512
width = 512
tot_pixels = height*width

def main():

	#os.path.dir(path_to_folder)
	#os.path.dir(dest_path)
	#Thresholds can be changed.
	
	#t0 = time.time()
	images = os.listdir(path_to_folder)
	pool = Pool()
	pool.map(work, images)
	pool.close()
	pool.join()
	#t1 = time.time()
	#print t1-t0

#sends in a list of images 
def work(image):
# If the images is not in the .png format just add the condition to the following if-statement with the extention of file.
	if image.endswith('.png'):
		path_to_image = path_to_folder + '/' + image
		img = cv2.imread(path_to_image)
		no_blue = count_pixels(img,height,width)
		percent_blue = no_blue/float(tot_pixels) 
	#percent_green = no_green/float(tot_pixels)
	#percent_bad = (no_green + no_blue)/float(tot_pixels)
	#print percent_blue, percent_green
	if percent_blue > thres_blue:
		shutil.move(path_to_image, dest_path)

def count_pixels(img, height, width):
	no_blue_pixels = 0
	#no_green_pixels = 0
	for i in range (0,height):
		for j in range(0,width):
			b,g,r = img[i,j]
			if b > (r + 10) and b > (g + 10):
				no_blue_pixels += 1
			#if g > (r + 10) and g > (b + 10) :
				#no_green_pixels += 1
	return no_blue_pixels#, no_green_pixels


if __name__ == '__main__':
	main()