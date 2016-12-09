
# This script takes images in a directory and resize them to wanted size to a folder that the user chooses
# It takes three inarguments: path to the images taken with the camera, save path to were the downsampled images should be saved, and the resolution of the image, the image will be quadratic

import os, math, sys
from PIL import Image
from resizeimage import resizeimage

def main(argv):
	#outputsize = 512; # Image size that the nerual network wants

	path_to_camera_images = sys.argv[1]
	save_path = sys.argv[2]
	outputsize = int(sys.argv[3])
	# check that the directory exists
	os.path.exists(path_to_camera_images)
	os.path.exists(save_path)

	# Get a list of images 
	list_of_images = get_files_from_dir(path_to_camera_images);

	# Read in each image and rezise, crop to wanted size and save in wanted directory
	for im in list_of_images:
		name = os.path.basename(im)
		save_path_name = save_path + name 
		fd_img = open(im, 'r')
		original = Image.open(fd_img)
		cropped = resize_image(original,outputsize)
		cropped.save(save_path_name)
		fd_img.close()
		

# Returns a list of file names of images in a directory
def get_files_from_dir(path_to_camera_images):
	lists_of_files = [];
	for file in os.listdir(path_to_camera_images):
		full_path = "";
		if file.endswith(".jpg") or file.endswith(".JPEG") or file.endswith(".png") or file.endswith(".PNG"):
			full_path = path_to_camera_images + "/" +file;
			lists_of_files.append(full_path);
	return lists_of_files

# Returns a resized 512 x 512 image
def resize_image(img, output_val):
	tmp_img = resizeimage.resize_width(img, output_val)
	width = tmp_img.size[0]
	height = tmp_img.size[1]

	if height > width: # A long image
		minY, maxY = min_max_values(height,output_val)
		tmp_img = tmp_img.crop((0,minY,output_val,maxY))

	elif width > height: # Wide image
		tmp_img = resizeimage.resize_height(img,output_val)
		width = tmp_img.size[0]
		minX, maxX = min_max_values(width,output_val)
		tmp_img = tmp_img.crop((minX,0,maxX,output_val))

	return tmp_img
	
# Finds the difference between the other side of the image and outputval
# Returns the min and max vaules
def min_max_values(value, output_val):
	diff = abs(output_val-value)
	min_val = math.floor(diff/2) 
	max_val = output_val + math.ceil(diff/2)

	return min_val, max_val



if __name__ == "__main__":
    main(sys.argv[1:])