#!/bin/bash


source /sonas-hs/it/hpc/home/easybuild/lmod-setup.sh
module load foss/2017b
module load TensorFlow/1.5.0-Python-3.6.3

BRAINNO=$1
LIST_DIR=$2
OUTPUT_DIR=$3
which python

python /sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/bins/1.Preprocessing/codes/CreateImg.py $BRAINNO $LIST_DIR $OUTPUT_DIR
