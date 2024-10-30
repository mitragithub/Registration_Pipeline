#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

mode=$1
brain=$2
PIPELINE_DIR=/nfs/data/main/M32/STP_RegistrationData/
BASELOC=$PIPELINE_DIR/bins/2.LddmmRegistration/
SCRIPTS_DIR=$BASELOC/scripts/
OUTPUT_DIR=$PIPELINE_DIR/data/transfer_para/
LIST_DIR=$PIPELINE_DIR/Lists

QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

# echo " 1.StackAlignNew PIPELINE Running for $BRAINNO ($NOW)"
# echo "****Step 2: =========== Dispatch to bnb for alignment ===="

if [ $mode == '-single' ]
    then
        python $BASELOC/codes/Registration.py $brain $PIPELINE_DIR

fi

if [ $mode == '-list' ]
    then
        cat $brain | while read LINE; do
            echo $LINE
            python $BASELOC/codes/Registration.py $LINE $PIPELINE_DIR
        done
fi

# $QSUB -pe threads 16 -l m_mem_free=2G -o $PIPELINE_DIR/data/bnb_outputs/${BRAINNO}_LDDMM_${NOW}.txt -e $PIPELINE_DIR/data/bnb_errors/${BRAINNO}_LDDMM_${NOW}.txt $SCRIPTS_DIR/LDDMM.sh $BRAINNO

