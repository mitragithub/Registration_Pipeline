import sys
import numpy as np # for arrays
#%matplotlib inline
import matplotlib as mpl # for graphics
import matplotlib.pyplot as plt
import nibabel as nib # for loading neuroimages
import lddmm_NN # algorithm
import vis # visualization
import tensorflow as tf
import basic_vtk_io as vtk
import os
import warnings
import  _pickle as cpickle
import SimpleITK as sitk
os.environ["CUDA_VISIBLE_DEVICES"]=""


def main():
    BRAINNO=sys.argv[1]
    BRAINNO=BRAINNO[0:6]
    # registration_pipeline_dir = sys.argv[2]
    registration_pipeline_dir = '/nfs/data/main/M32/STP_RegistrationData'
    print(registration_pipeline_dir + '/data/transfer_para/' + BRAINNO + '.pickle')
    with open(registration_pipeline_dir + '/data/transfer_para/' + BRAINNO + '.pickle', 'rb') as f:
        out = cpickle.load(f)


    atlas_image_fname = registration_pipeline_dir + '/ATLAS/average_template_50.vtk'
    target_image_fname = registration_pipeline_dir + '/data/preprocessing/' + BRAINNO + '_50.img'

    x0I,x1I,x2I,I,title,names = vtk.read_vtk_image(atlas_image_fname)
    # convert to mm
    x0I /= 1000.0
    x1I /= 1000.0
    x2I /= 1000.0


    xI_50 = [x0I,x1I,x2I]
    nxI = np.array(I.shape[:3])
    dxI = np.array([x0I[1]-x0I[0], x1I[1]-x1I[0], x2I[1]-x2I[0]])
    I = I.squeeze()

    img = nib.load(target_image_fname)
    J = np.array(img.get_data()).squeeze()
    nxJ = np.array(img.header['dim'][1:4])
    dxJ = np.array(img.header['pixdim'][1:4])
    xJ_50 = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJ,dxJ)]


    # pad so that there is a black boundary, this improves extrapolation when deforming the Allen atlas
    npad = 10
    I = np.pad(I,npad,mode='constant',constant_values=0)
    nxI += npad*2
    xI_50 = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]

###############
    atlas_image_fname = registration_pipeline_dir + '/ATLAS/average_template_10.vtk'
    target_image_fname = registration_pipeline_dir + '/data/preprocessing/' + BRAINNO + '_10.img'

    x0I,x1I,x2I,I,title,names = vtk.read_vtk_image(atlas_image_fname)
    # convert to mm
    x0I /= 1000.0
    x1I /= 1000.0
    x2I /= 1000.0


    xI = [x0I,x1I,x2I]
    nxI = np.array(I.shape[:3])
    dxI = np.array([x0I[1]-x0I[0], x1I[1]-x1I[0], x2I[1]-x2I[0]])
    I = I.squeeze()

    img = nib.load(target_image_fname)
    J = np.array(img.get_data()).squeeze()
    # J = np.asarray(J, dtype='float32')

    nxJ = np.array(img.header['dim'][1:4])
    dxJ = np.array(img.header['pixdim'][1:4])
    xJ = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJ,dxJ)]


    # pad so that there is a black boundary, this improves extrapolation when deforming the Allen atlas
    # npad = 10
    # I = np.pad(I,npad,mode='constant',constant_values=0)
    # nxI += npad*2
    # xI = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]



    xS = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]

    xS = xI
    JD = lddmm_NN.transform_data(xJ[0],xJ[1],xJ[2],J,out['Aphi0'],out['Aphi1'],out['Aphi2'],
                    y=xI, # sample points
                    t=xI_50 # transformation is sampled at these points
                    )

    # JD = lddmm.transform_data(xI[0],xI[1],xI[2],I,out['phiinvAinv0'],out['phiinvAinv1'],out['phiinvAinv2'],
    #                 y=xJ, # sample points
    #                 t=xJ_50, # transformation is sampled at these points
    #                 method=0
    #                 )
    registerd = sitk.GetImageFromArray(JD)
    registerd.SetSpacing((0.01, 0.01, 0.05))
    registerd.SetOrigin((0,0,0))
    sitk.WriteImage(registerd, registration_pipeline_dir + '/data/deformedTarget/' + BRAINNO + '_atlas_10.img')


if __name__ == "__main__":
    main()


