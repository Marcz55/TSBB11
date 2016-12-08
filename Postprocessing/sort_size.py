# This scrip goes thorugh a directory with rendered images and saves those images that are useful in a subfolder called "good images"

import os, sys, shutil
import numpy as np
import pdb


def main(argv):
	path_to_folder = sys.argv[1]
	size_of_im = sys.argv[2]
	save_path = sys.argv[3]
	# check that the path exists
	os.path.exists(path_to_folder)

	sort_out_small_images(path_to_folder, save_path , size_of_im)


# Function that takes in the full paths to all images in a folder , a save path and copies all the images larger than a certain size of image
# returns nothing
def sort_out_small_images(path_to_folder, save_path, size_of_im):
	list_of_images = os.listdir(path_to_folder)
	for file in list_of_images:
		location = os.path.join(path_to_folder,file)
		size = os.path.getsize(location)
		if size > int(size_of_im):
			full_save_path = os.path.join(save_path,file)
			shutil.copyfile(location,full_save_path)

if __name__ == "__main__":
    main(sys.argv[1:])