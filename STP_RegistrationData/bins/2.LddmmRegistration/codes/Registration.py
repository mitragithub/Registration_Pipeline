import numpy as np # for arrays
import matplotlib as mpl # for graphics
import nibabel as nib # for loading neuroimages
import lddmm # algorithm
import vis # visualization
import tensorflow as tf
import imp # use imp.reload to update modules during development
import SimpleITK as sitk
import os
import pickle
import matplotlib.pyplot as plt
import sys
import basic_vtk_io as vtk
os.environ["CUDA_VISIBLE_DEVICES"]=""
#matplotlib.use('Agg')

def main():
    BRAINNO=sys.argv[1]
    BRAINNO=BRAINNO[0:6]
    registration_pipeline_dir = sys.argv[2]
    atlas_image_fname = registration_pipeline_dir + '/ATLAS/average_template_50.vtk'
    target_image_fname = registration_pipeline_dir + '/data/preprocessing/' + BRAINNO +'_50.img'

    gamma = 0.25
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
    themax = np.max(J)
    J = J/themax
    J **= gamma
    J *= themax

    nxJ = np.array(img.header['dim'][1:4])
    dxJ = np.array(img.header['pixdim'][1:4])
    xJ = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJ,dxJ)]

    # pad so that there is a black boundary, this improves extrapolation when deforming the Allen atlas
    # I should pad enough that the downsampled image is also padded
    # but I may want to pad even more
    npad = 4
    npad = 10 # even more
    I = np.pad(I,npad,mode='constant',constant_values=0)
    nxI += npad*2
    xI = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]

    # the line below is a good initial orientation
    A = np.array([[0,0,1,0],
                [0,1,0,0],
                [1,0,0,0],
                [0,0,0,1]])
    A = np.array([[1,0,0,0],
                [0,0,1,0],
                [0,1,0,0],
                [0,0,0,1]])@A
    A = np.diag([-1,1,-1,1])@A


    # test the initial affine
    Idnp = lddmm.affine_transform_data(*xI,I,A,*xJ)

    f = plt.figure()
    vis.imshow_slices(Idnp,x=xJ,fig=f)
    f.suptitle('Initial affine transformation')
    f.canvas.draw()
########################start lddmm###########################################
    # first low res
    down = 4
    Id = lddmm.down(I,[down,down,down])
    dxId = dxI*down
    nxId = np.array(Id.shape)
    xId = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxId,dxId)]

    Jd = lddmm.down(J,[down,down,down])
    dxJd = dxJ*down
    nxJd = np.array(Jd.shape)
    xJd = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJd,dxJd)]

    # parameters
    # cost function weights 1 / sigma^2
    sigmaM = np.std(Jd) # matching
    sigmaA = sigmaM*10.0 # artifact
    sigmaR = 2e0 # regularization (increased this parameter from 1e0) (done and visualized)
    sigmaR = 5e0 # running on july 25
    sigmaR = 1e1 # running july 25 evening
    sigmaR = 1e2 # running july 26 morning
    sigmaR = 2e1 # july 26 afternoon

    # now with gamma 0.25
    sigmaR = 2e0


    # enery operator, power of laplacian p, characteristic length a
    p = 2
    a = (xI[0][1]-xI[0][0])*5 # this is a smoothness of 5 pixels at full resolution

    # other optimization parameters
    nt = 5 # this many timesteps to numerically integrate flow
    # the linear part is a bit too big still (since I fixed voxel size issue)
    # initial guess for affine (check picture above)
    A0 = A



    # reduce M step iterations, in EM algorithm.  I have found they do not improve things.
    nMstep = 1
    nMstep_affine = 1
    eV0 = 1e-2
    eL0 = 1e-4
    eT0 = 5e-4


    eL = eL0*down
    eT = eT0*down
    eV = 0.0
    niter = 100
    naffine = 100

    # trying to double the iters, reduce the affine a bit
    niter = 200
    naffine = 200
    eV0 = 1e-2
    eL0 = 5e-5
    eT0 = 2e-4
    # try to make ev a bit bigger, it really hasn't converged yet
    eV0 = 2e-2

    eV = 0.0
    eL = eL0*down
    eT = eT0*down

    out_d4_affine = lddmm.lddmm(Id, Jd, 
                    xI=xId, # location of pixels in domain
                    xJ=xJd,                  
                    niter=niter, # iterations of gradient descent
                    naffine=naffine, # iterations of affine only
                    eV=eV, # step size for deformation parameters
                    eT=eT, # step size for translation parameters
                    eL=eL, # step size for linear parameters
                    nt=nt, # timesteps for integtating flow
                    sigmaM=sigmaM, # matching cost weight 1/2sigmaM^2
                    sigmaR=sigmaR, # reg cost weight 1/2sigmaM^2
                    sigmaA=sigmaA, # artifact cost weight 1/2sigmaA^2
                    a=a, # kernel width
                    p=p, # power of laplacian in kernel (should be at least 2 for 3D)
                    A0=A0, # initial guess for affine matrix (should get orientation right)
                    nMstep=nMstep, # number of m steps for each e step
                    nMstep_affine=nMstep_affine # number of m steps during affine only phase
                    )

    # now we'll include deformation
    niter = 200
    naffine = 0
    eV = eV0*down
    eL = eL0*down
    eT = eT0*down

    out_d4 = lddmm.lddmm(Id, Jd, 
                    xI=xId, # location of pixels in domain
                    xJ=xJd,                  
                    niter=niter, # iterations of gradient descent
                    naffine=naffine, # iterations of affine only
                    eV=eV, # step size for deformation parameters
                    eT=eT, # step size for translation parameters
                    eL=eL, # step size for linear parameters
                    nt=nt, # timesteps for integtating flow
                    sigmaM=sigmaM, # matching cost weight 1/2sigmaM^2
                    sigmaR=sigmaR, # reg cost weight 1/2sigmaM^2
                    sigmaA=sigmaA, # artifact cost weight 1/2sigmaA^2
                    a=a, # kernel width
                    p=p, # power of laplacian in kernel (should be at least 2 for 3D)
                    A0=out_d4_affine['A'], # initial guess for affine matrix (should get orientation right)
                    nMstep=nMstep, # number of m steps for each e step
                    nMstep_affine=nMstep_affine # number of m steps during affine only phase
                    )

    # now higher res
    down = 2
    Id = lddmm.down(I,[down,down,down])
    dxId = dxI*down
    nxId = np.array(Id.shape)
    xId = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxId,dxId)]

    Jd = lddmm.down(J,[down,down,down])
    dxJd = dxJ*down
    nxJd = np.array(Jd.shape)
    xJd = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJd,dxJd)]

    niter = 100
    naffine = 0
    eV = eV0*down
    eL = eL0*down
    eT = eT0*down

    out_d2 = lddmm.lddmm(Id, Jd, 
                    xI=xId, # location of pixels in domain
                    xJ=xJd,                  
                    niter=niter, # iterations of gradient descent
                    naffine=naffine, # iterations of affine only
                    eV=eV, # step size for deformation parameters
                    eT=eT, # step size for translation parameters
                    eL=eL, # step size for linear parameters
                    nt=nt, # timesteps for integtating flow
                    sigmaM=sigmaM, # matching cost weight 1/2sigmaM^2
                    sigmaR=sigmaR, # reg cost weight 1/2sigmaM^2
                    sigmaA=sigmaA, # artifact cost weight 1/2sigmaA^2
                    a=a, # kernel width
                    p=p, # power of laplacian in kernel (should be at least 2 for 3D)
                    A0=out_d4['A'], # initial guess for affine matrix (should get orientation right)
                    vt00 = out_d4['vt0'],
                    vt10 = out_d4['vt1'],
                    vt20 = out_d4['vt2'],
                    nMstep=nMstep, # number of m steps for each e step
                    nMstep_affine=nMstep_affine # number of m steps during affine only phase
                    )
    # now full res
    niter = 50
    naffine = 0
    out_d1 = lddmm.lddmm(I, J, 
                    xI=xI, # location of pixels in domain
                    xJ=xJ,                  
                    niter=niter, # iterations of gradient descent
                    naffine=naffine, # iterations of affine only
                    eV=eV0, # step size for deformation parameters
                    eT=eT0, # step size for translation parameters
                    eL=eL0, # step size for linear parameters
                    nt=nt, # timesteps for integtating flow
                    sigmaM=sigmaM, # matching cost weight 1/2sigmaM^2
                    sigmaR=sigmaR, # reg cost weight 1/2sigmaM^2
                    sigmaA=sigmaA, # artifact cost weight 1/2sigmaA^2
                    a=a, # kernel width
                    p=p, # power of laplacian in kernel (should be at least 2 for 3D)
                    A0=out_d2['A'], # initial guess for affine matrix (should get orientation right)
                    vt00 = out_d2['vt0'],
                    vt10 = out_d2['vt1'],
                    vt20 = out_d2['vt2'],
                    nMstep=nMstep, # number of m steps for each e step
                    nMstep_affine=nMstep_affine # number of m steps during affine only phase
                    )
    import  _pickle as cpickle
    with open(registration_pipeline_dir+'/data/transfer_para/' + BRAINNO +'.pickle', 'wb') as f:
        cpickle.dump(out_d1, f)

if __name__ == "__main__":
    main()

