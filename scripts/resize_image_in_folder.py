
from os import listdir
from os.path import isfile, join
import argparse
import numpy as np
import cv2

parser = argparse.ArgumentParser(description="Resizes images in a directory")
parser.add_argument("--image_path", type=str, required = True)
args = parser.parse_args()
image_path = args.image_path;

files = [f for f in listdir(image_path) if isfile(join(image_path,f))];
for infile in files:
    image = cv2.imread(image_path+"/"+infile)
    print(image_path+"/"+infile)
    resized_image = cv2.resize(image, (455, 256))
    cv2.imwrite(image_path + "/resized_" + infile, resized_image)
    
