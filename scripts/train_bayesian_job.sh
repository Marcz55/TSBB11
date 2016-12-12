#!/bin/bash
#
#SBATCH -J train_bayesian
#SBATCH -A snic2016-5-43
#SBATCH -t 08:00:00
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH --reservation=gpu
#SBATCH --gres=gpu:1
#

source /proj/camerapose/startup7
python /proj/camerapose/custom/scripts/train_bayesian.py