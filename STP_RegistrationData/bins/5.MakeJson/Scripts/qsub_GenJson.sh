#! /opt/hpc/bin/bash
if (($# < 1))
then
    echo "No brainname argument... exiting"
    exit 1
fi

date
source /sonas-hs/it/hpc/home/easybuild/lmod-setup.sh
module load foss/2016a
module load IntelPython/2.7.12

BRAINNO=$1
PIPELINE_DIR=/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/
BASELOC=$PIPELINE_DIR/bins/5.MakeJson/

python $BASELOC/codes/brain_region.py $BRAINNO


date
