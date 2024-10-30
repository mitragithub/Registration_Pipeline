#!/bin/bash
if (($# < 1))
then
    echo "No input brainname argument... exiting"
    exit 1
fi

mode=$1
BRAINNO=$2
PIPELINE_DIR=/nfs/data/main/M32/STP_RegistrationData/
# BASELOC=$PIPELINE_DIR/bins/3.Transformation/
# SCRIPTS_DIR=$BASELOC/scripts/
# OUTPUT_DIR=$PIPELINE_DIR/data/transformation/
# LIST_DIR=$PIPELINE_DIR/Lists

# QSUB=/opt/uge/bin/lx-amd64/qsub

NOW=`date +%d-%m-%y_%H%M`

# echo " 1.StackAlignNew PIPELINE Running for $BRAINNO ($NOW)"
# echo "****Step 2: =========== Dispatch to bnb for alignment ===="



# $QSUB -pe threads 8 -l m_mem_free=2G -o $PIPELINE_DIR/data/bnb_outputs/${BRAINNO}_transformation_${NOW}.txt -e $PIPELINE_DIR/data/bnb_errors/${BRAINNO}_transformation_${NOW}.txt $SCRIPTS_DIR/transformation.sh $BRAINNO

if [ $mode == '-single' ]
    then
        mkdir -p $PIPELINE_DIR/data/toPortal/FIX_$BRAINNO
        # python $PIPELINE_DIR/bins/3.Transformation/Combine_Color.py $BRAINNO
        cp /nfs/data/main/M*/jhuangU19/level_1/${BRAINNO}_*/stitchedImage_ch2/*.tif $PIPELINE_DIR/data/toPortal/FIX_$BRAINNO/
        #rotate and jp2 compression
        for filename in $PIPELINE_DIR/data/toPortal/FIX_$BRAINNO/*.tif; do
            convert "${filename//.tif}.tif" -rotate 180 "${filename//.tif}.tif"
            # kdu_compress -i "${filename//.tif}.tif" -o "${filename//.tif}.jp2" -num_threads 16 -rate 1.0 Creversible=yes Sprecision=16 Ssigned=no -full -precise Clevels=7 Clayers=8 Qstep=0.00001 Cblk=\{64,64\} Corder=RPCL Cuse_sop=yes ORGgen_plt=yes ORGtparts=R

        done
        #thumbnail
        # for filename in $PIPELINE_DIR/data/toPortal/HUA_$BRAINNO/*.jp2; do
        #     kdu_expand -i "$filename" -o "${filename//.jp2}.tif" -reduce 6 -num_threads 16
        #     convert "${filename//.jp2}.tif" -evaluate Multiply 32 -depth 8 "${filename//.jp2}.jpg"
        # done
        # rm -rf $PIPELINE_DIR/data/toPortal/HUA_$BRAINNO/*.tif
        # ls $PIPELINE_DIR/data/toPortal/HUA_$BRAINNO/*.jp2|wc -l >> $PIPELINE_DIR/data/toPortal/HUA_$BRAINNO/Count.txt
fi




