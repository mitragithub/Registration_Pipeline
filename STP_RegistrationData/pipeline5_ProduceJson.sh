#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi
mode=$1
brain=$2

PIPELINE_DIR=/nfs/data/main/M32/STP_RegistrationData/
BASELOC=$PIPELINE_DIR/bins/5.MakeJson/
SCRIPTS_DIR=$BASELOC/Scripts/
# OUTPUT_DIR=$PIPELINE_DIR/data/transformation/
LIST_DIR=$PIPELINE_DIR/Lists

QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

# echo " 1.StackAlignNew PIPELINE Running for $BRAINNO ($NOW)"
# echo "****Step 2: =========== Dispatch to bnb for alignment ===="



# $QSUB -pe threads 8 -l m_mem_free=7G -o $PIPELINE_DIR/data/bnb_outputs/${BRAINNO}_Json_${NOW}.txt -e $PIPELINE_DIR/data/bnb_errors/${BRAINNO}_Json_${NOW}.txt $SCRIPTS_DIR/qsub_GenJson.sh $BRAINNO

if [ $mode == '-single' ]
    then
        python $BASELOC/codes/brain_region.py $brain
fi

if [ $mode == '-list' ]
    then
        cat $brain | while read LINE; do
            echo $LINE
            python $BASELOC/codes/brain_region.py $LINE
        done
fi

