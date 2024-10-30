#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

mode=$1
brain=$2

PIPELINE_DIR=/nfs/data/main/M32/STP_RegistrationData/
BASELOC=$PIPELINE_DIR/bins/3.Transformation/
SCRIPTS_DIR=$BASELOC/scripts/
OUTPUT_DIR=$PIPELINE_DIR/data/transfer_para/
LIST_DIR=$PIPELINE_DIR/Lists


if [ $mode == '-single' ]
    then
        python $BASELOC/codes/TransferAtlas50.py $brain $PIPELINE_DIR

fi

if [ $mode == '-list' ]
    then
        cat $brain | while read LINE; do
            echo $LINE
            python $BASELOC/codes/TransferAtlas50.py $LINE $PIPELINE_DIR
        done
fi
