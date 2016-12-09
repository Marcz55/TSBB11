import cv2,sys
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
def apply_color_transform(im_raw, color_transform):
	# im_raw of shape (3, 256, 455)
	#    import matplotlib.pyplot as plt
	# Make it RGB
	im_raw_rgb = np.zeros(im_raw.shape)
	im_raw_rgb[0,:,:] = im_raw[2,:,:]
	im_raw_rgb[1,:,:] = im_raw[1,:,:]
	im_raw_rgb[2,:,:] = im_raw[0,:,:]
	#    plt.imshow(np.moveaxis(im_raw_rgb,0,-1))
	#    plt.show()
	#    print(color_transform)
	# Apply color transform pixel-wise
	im0 = im_raw_rgb.reshape((3,im_raw.shape[1]*im_raw.shape[2]))
	im1 = np.dot(color_transform, im0)
	im2 = im1.reshape((3,im_raw.shape[1],im_raw.shape[2]))
	#    print(im2[:,10,150]/256)
	#plt.imshow(np.moveaxis(im2/256,0,-1))
	#plt.show()
	#plt.savefig("tmp.jpg")


	# Make it BGR again
	im3 = np.zeros(im2.shape)
	im3[0,:,:] = im2[2,:,:]
	im3[1,:,:] = im2[1,:,:]
	im3[2,:,:] = im2[0,:,:]
	return im3

def read_mat_from_txt(path):
	f = open(path)
	# @todo should check f viability here
	mat = np.zeros((3,3))
	row = 0
	for line in f:
		tokens = line.rstrip('\n').split(' ')
		for col in range(0,len(tokens)):
			mat[row,col] = tokens[col]
		row = row + 1
	return mat

def main(args):
	image_path = sys.argv[1]
	color_transform_path = sys.argv[2]

	#color_transform = read_mat_from_txt(image_path+"/color_transform.dat")
	#im_raw = np.moveaxis(cv2.imread(image_path), -1, 0)

	color_transform = read_mat_from_txt(color_transform_path)
	im_raw = np.moveaxis(cv2.imread(image_path), -1, 0)
	im_color_transformed = apply_color_transform(im_raw, color_transform)
	print im_color_transformed.shape
	#cv2.imwrite('tmp.jpg',im_color_transformed)


if __name__ == '__main__':
	main(sys.argv[1:])