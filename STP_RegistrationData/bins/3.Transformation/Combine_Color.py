import numpy as np
import glob
import skimage.io
import os
from multiprocessing import Pool
import sys
import re

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


BRAINNO = sys.argv[1]
PIPELINE_DIR='/nfs/data/main/M32/STP_RegistrationData/'

def Color_Combine_Single_Section(ch1):
    ch2 = ch1.replace("_ch1", "_ch2")
    
    # Gpath = '/nfs/data/main/M31/MouseExtramuralData/fMOST/732706821/green/'
    # Rpath = '/nfs/data/main/M31/MouseExtramuralData/fMOST/732706821/red/'
    # RGBpath = '/nfs/data/main/M31/MouseExtramuralData/fMOST/732706821/RGB/'
    basename = os.path.basename(ch1)
    r = skimage.io.imread(ch1)
    g = skimage.io.imread(ch2)
    r = np.asarray(r, dtype = 'uint16')
    g = np.asarray(g, dtype = 'uint16')
    b = np.zeros((r.shape[0], r.shape[1]), dtype = 'uint16')
    img = np.dstack((r,g,b))
    print(basename)
    skimage.io.imsave(PIPELINE_DIR + '/data/toPortal/HUA_' + BRAINNO + \
                        '/' + basename, img)
    # os.system('kdu_compress -i ' + RGBpath + basename + ' -o ' + \
    #          RGBpath + basename[:-3] + 'jp2' + \
    #          ' -rate 0.1 Creversible=yes Clevels=7 Clayers=8 Stiles=\{1024,1024\} \
    #          Corder=RPCL Cuse_sop=yes ORGgen_plt=yes ORGtparts=R Cblk=\{32,32\} -num_threads 32')

    # os.system('convert ' + RGBpath + basename+' -evaluate Multiply 128 -depth 8 \
    #          -resize 1% ' + RGBpath + basename[:-3] + 'jpg')

    # os.system('rm -rf ' + RGBpath + basename)


def main():
    ch1List = natural_sort(glob.glob('/nfs/data/main/*/jhuangU19/level_1/' \
            + BRAINNO + '_*/stitchedImage_ch1/*.tif'))
    # print(ch1List[100])
    # Color_Combine_Single_Section(ch1List[100])
    with Pool(16) as p:
        p.map(Color_Combine_Single_Section, ch1List)
if __name__ == "__main__":
    # execute only if run as a script
    main()
