#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

BRAINNO=$1

PIPELINE_DIR=/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/

QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

$QSUB -pe threads 16 -l m_mem_free=4G -o $PIPELINE_DIR/data/bnb_outputs/${BRAINNO}_X_${NOW}.txt -e $PIPELINE_DIR/data/bnb_errors/${BRAINNO}_X_${NOW}.txt $PIPELINE_DIR/OneRingToRuleThemALL.sh $BRAINNO

