# Make sure that caffe is on the python path:
import sys
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
import sys

caffe_path="/proj/camerapose/posenet/caffe-posenet/build/tools/caffe"
solver_path="/proj/camerapose/custom/scripts/models/solver_bayesian_posenet.prototxt"
snapshot_path=""
mode="new"

caffe.set_mode_gpu()

if mode == "resume":
  proc = subprocess.Popen(
      [caffe_path,"train","--solver=" + solver_path,"--snapshot=" + snapshot_path], 
      stderr=subprocess.PIPE)
  res = proc.communicate()[1]
else:
  proc = subprocess.Popen(
      [caffe_path,"train","--solver=" + solver_path], 
      stderr=subprocess.PIPE)
  res = proc.communicate()[1]

solver = caffe.get_solver(solver_path)
solver.solve()

print res

