#!/bin/bash


source /sonas-hs/it/hpc/home/easybuild/lmod-setup.sh
module load foss/2016a
module load IntelPython/2.7.12
GLIBC_DIR=/sonas-hs/mitra/hpc/home/xli/glibc-2.17-install/lib
alias tfpython="$GLIBC_DIR/ld-2.17.so --library-path $GLIBC_DIR:/lib64:$LD_LIBRARY_PATH /sonas-hs/it/hpc/home/easybuild/install_prod/software/MPI/GCC/4.9.3-2.25/OpenMPI/1.10.2/IntelPython/2.7.12/bin/python"

BRAINNO=$1

#tfpython 
$GLIBC_DIR/ld-2.17.so --library-path $GLIBC_DIR:/lib64:$LD_LIBRARY_PATH /sonas-hs/it/hpc/home/easybuild/install_prod/software/MPI/GCC/4.9.3-2.25/OpenMPI/1.10.2/IntelPython/2.7.12/bin/python /sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/bins/2.LddmmRegistration/codes/Registration.py $BRAINNO
