#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

# BRAINNO=$1
mode=$1
brain=$2
PIPELINE_DIR=/nfs/data/main/M32/STP_RegistrationData/
BASELOC=$PIPELINE_DIR/bins/1.Preprocessing/
SCRIPTS_DIR=$BASELOC/scripts/
OUTPUT_DIR=$PIPELINE_DIR/data/preprocessing/
LIST_DIR=$PIPELINE_DIR/Lists

QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

# echo " 1.StackAlignNew PIPELINE Running for $BRAINNO ($NOW)"
# echo "****Step 2: =========== Dispatch to bnb for alignment ===="

python $BASELOC/codes/CreateImg.py $mode $brain $LIST_DIR $OUTPUT_DIR

