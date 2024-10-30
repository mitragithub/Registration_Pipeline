#Create downsampled image for registration
import numpy as np
import cv2
import glob
import re
import SimpleITK as sitk
import skimage
import sys
import os

def main():
    # BRAINNO = sys.argv[1]
    # LIST_DIR = sys.argv[2]
    # OUTPUT_DIR = sys.argv[3]
    mode = sys.argv[1]
    if mode == '-single':
        BRAINNO = sys.argv[2]
        LIST_DIR = sys.argv[3]
        OUTPUT_DIR = sys.argv[4]

        with open(LIST_DIR + '/' + BRAINNO + '_List.txt') as f:
            lines = f.read().splitlines()

        original_res = 1 #change this if original resolution is changed.
        target_res = 10 #change this to atlas resolution if needed

        imgstack = []
        for element in lines:
            body = os.path.basename(element)[0:-4]
            try:
                img_path = '/nfs/data/main/M32/STP_RegistrationData/data/TEMP/' + body + '_detects.jpg'
                img = cv2.imread(img_path, -1)
                if img.ndim == 3:
                    img = img[:,:,0]
                print(body)
                print(img.shape)
                imgDown = skimage.transform.resize(img, (int(img.shape[0] * original_res / target_res), 
                                                int(img.shape[1] * original_res / target_res)), order=0)
                imgDown = np.asarray(imgDown * 255, dtype = 'uint8')
                imgstack.append(imgDown)
            except:
                print(body + ' not work')
                img = np.zeros((11377, 8557))
                print(img.shape)
                imgDown = skimage.transform.resize(img, (int(img.shape[0] * original_res / target_res), 
                                                int(img.shape[1] * original_res / target_res)), order=0)
                imgDown = np.asarray(imgDown * 255, dtype = 'uint8')
                imgstack.append(imgDown)
        imgstack = np.asarray(imgstack)
        imgstack = np.swapaxes(imgstack, 0, 1)
        imgstack = np.swapaxes(imgstack, 1, 2)


        sitkimg = sitk.GetImageFromArray(imgstack)
        sitkimg.SetSpacing((0.05, 0.01, 0.01)) #change this if atlas is changed
        sitkimg.SetOrigin((0.0, 0.0, 0.0))

        sitk.WriteImage(sitkimg, OUTPUT_DIR + '/' + BRAINNO + '_10.img')

if __name__ == "__main__":
    main()