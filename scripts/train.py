import subprocess
import numpy as np
import caffe
import matplotlib.pyplot as plt
import os.path
import json
import scipy
import argparse
import math
import pylab
from sklearn.preprocessing import normalize
from mpl_toolkits.mplot3d import Axes3D

# Make sure that caffe is on the python path:
#caffe_root = '.../caffe-posenet/'  # Change to your directory to caffe-posenet
import sys
#sys.path.insert(0, caffe_root + 'python')

#import caffe

# Import arguments
caffe.set_mode_gpu()



proc = subprocess.Popen(
    ["/proj/camerapose/posenet/caffe-posenet/build/tools/caffe","train","--solver=/proj/camerapose/custom/scripts/models/solver_posenet.prototxt"], 
    stderr=subprocess.PIPE)
res = proc.communicate()[1]


solver = caffe.get_solver("/proj/camerapose/custom/scripts/models/solver_posenet.prototxt")
solver.solve()

print res

