#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

BRAINNO=$1

PIPELINE_DIR=/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/
BASELOC=$PIPELINE_DIR/bins/3.Transformation/
SCRIPTS_DIR=$BASELOC/scripts/
OUTPUT_DIR=$PIPELINE_DIR/data/transformation/
LIST_DIR=$PIPELINE_DIR/Lists

QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

# echo " 1.StackAlignNew PIPELINE Running for $BRAINNO ($NOW)"
# echo "****Step 2: =========== Dispatch to bnb for alignment ===="



$QSUB -pe threads 8 -l m_mem_free=2G -o $PIPELINE_DIR/data/bnb_outputs/${BRAINNO}_transformation_${NOW}.txt -e $PIPELINE_DIR/data/bnb_errors/${BRAINNO}_transformation_${NOW}.txt $SCRIPTS_DIR/transformation.sh $BRAINNO

