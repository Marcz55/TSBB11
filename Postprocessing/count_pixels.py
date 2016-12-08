import cv2

def main():
	img = cv2.imread('TRtest_x104_y24_a44_t-14.png')
	height, width = img.shape[:2]
	tot = width*height
	blue ,green = count_pixels(img,height,width)
	procent_blue = blue/float(tot)
	procent_green = green/float(tot)
	print procent_blue, procent_green

def count_pixels(img, height, width):
	no_blue_pixels = 0
	no_green_pixels = 0
	for i in range (0,height):
		for j in range(0,width):
			b,g,r = img[i,j]
			if b > r and b > g:
				no_blue_pixels += 1
			if g > r and g > b:
				no_green_pixels += 1
	return no_blue_pixels, no_green_pixels

if __name__ == '__main__':
	main()