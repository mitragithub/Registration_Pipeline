import numpy as np # for arrays
import matplotlib as mpl # for graphics
#import matplotlib.pyplot as plt
import nibabel as nib # for loading neuroimages
import lddmm # algorithm
import vis # visualization
import tensorflow as tf
import imp # use imp.reload to update modules during development
import SimpleITK as sitk
import os
import pickle
import matplotlib
import sys
#matplotlib.use('Agg')

def main():
    BRAINNO=sys.argv[1]
    registration_dir = '/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/'
    atlas_image_fname = '/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/template/average_template_50_rot.img'
    target_image_fname = '/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/data/preprocessing/' + BRAINNO + '_50.img'
    out = '/sonas-hs/mitra/hpc/home/hliu/public/STP_registration_pipeline/data/'

    targetNO = BRAINNO
    print targetNO

    atlas = sitk.ReadImage(atlas_image_fname)
    target = sitk.ReadImage(target_image_fname)

    print("ATLAS INFO")
    print(atlas.GetSize())
    print(atlas.GetSpacing())
    print(atlas.GetOrigin())
    print("TARGET INFO")
    print(target.GetSize())
    print(target.GetSpacing())
    print(target.GetOrigin())

    # load them with nibabel
    fnames = [atlas_image_fname,target_image_fname]
    img = [nib.load(fname) for fname in fnames]

    # get info about image space
    if '.img' == atlas_image_fname[-4:]:    
        nxI = img[0].header['dim'][1:4]
        dxI = img[0].header['pixdim'][1:4]
        nxJ = img[1].header['dim'][1:4]
        dxJ = img[1].header['pixdim'][1:4]
    else:
        # I'm only working with analyze for now
        raise ValueError('Only Analyze images supported for now')
    xI = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]
    xJ = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxJ,dxJ)]

    # get the images, note they also include a fourth axis for time that I don't want
    I = img[0].get_data()[:,:,:]
    J = img[1].get_data()[:,:,:]

    # I would like to pad one slice of the allen atlas so that it has zero boundary conditions
    zeroslice = np.zeros((nxI[0],1,nxI[2]))
    I = np.concatenate((I,zeroslice),axis=1)
    nxI = img[0].header['dim'][1:4]
    nxI[1] += 1
    xI = [np.arange(nxi)*dxi - np.mean(np.arange(nxi)*dxi) for nxi,dxi in zip(nxI,dxI)]

    # display the data
    #f = plt.figure()
    #vis.imshow_slices(I, x=xI, fig=f)
    #f.suptitle('Atlas I')
    #f.canvas.draw()
    # the line below is a good initial orientation
    A = np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])

    # test the initial affine
    X0,X1,X2 = np.meshgrid(xJ[0],xJ[1],xJ[2],indexing='ij')
    X0tf = tf.constant(X0,dtype=lddmm.dtype)
    X1tf = tf.constant(X1,dtype=lddmm.dtype)
    X2tf = tf.constant(X2,dtype=lddmm.dtype)
    Itf = tf.constant(I,dtype=lddmm.dtype)
    B = np.linalg.inv(A)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        Xs = B[0,0]*X0tf + B[0,1]*X1tf + B[0,2]*X2tf + B[0,3]
        Ys = B[1,0]*X0tf + B[1,1]*X1tf + B[1,2]*X2tf + B[1,3]
        Zs = B[2,0]*X0tf + B[2,1]*X1tf + B[2,2]*X2tf + B[2,3]
        Id = lddmm.interp3(xI[0], xI[1], xI[2], Itf, Xs, Ys, Zs)
        Idnp = Id.eval()
    #f = plt.figure()
    #vis.imshow_slices(Idnp,x=xJ,fig=f)
    #f.suptitle('Initial affine transformation')
    #f.canvas.draw()


    # parameters
    # cost function weights 1 / sigma^2
    sigmaM = np.std(J) # matching
    sigmaA = sigmaM*10.0 # artifact
    sigmaR = 1e0 # regularization

    # enery operator, power of laplacian p, characteristic length a
    p = 2
    a = (xI[0][1]-xI[0][0])*5

    # other optimization parameters
    niter = 500 # how many iteraitons of gradient descent
    naffine = 100 # first naffine iterations are affine only (no deformation)
    nt = 5 # this many timesteps to numerically integrate flow
    # the linear part is a bit too big still (since I fixed voxel size issue)
    # initial guess for affine (check picture above)
    A0 = A

    # When working with weights in EM algorithm, how many M steps per E step
    # first test with 0 (it is working)
    nMstep = 5
    nMstep_affine = 1

    # gradient descent step size
    eL = 2e-4
    eT = 5e-3
    eV = 5e-3
    # I think maybe eV has to be bigger
    eV = 1e-2
    # there is some oscilation in the translation and the linear part

    out = lddmm.lddmm(I, J, 
                    xI=xI, # location of pixels in domain
                    xJ=xJ,                  
                    niter=niter, # iterations of gradient descent
                    naffine=naffine, # iterations of affine only
                    eV = eV, # step size for deformation parameters
                    eT = eT, # step size for translation parameters
                    eL = eL, # step size for linear parameters
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

    os.system("mkdir " + registration_dir + "/data/transfer_para/" + targetNO)
    with open(registration_dir + "/data/transfer_para/" + targetNO + "/transfer_para.pickle", 'wb') as f:
        pickle.dump(out, f)
    print "Parameters saved. Existing..."
    
    out['f_kernel'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/kernel.png')
    out['f_deformed'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/atlas-deformed.png')
    out['f_error'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/error.png')
    out['f_energy'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/energy.png')
    if nMstep > 0:
        out['f_WM'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/atlas-weight.png')
        out['f_WA'].savefig(registration_dir + "/data/transfer_para/" + targetNO + '/artifact-weight.png')

if __name__ == "__main__":
    main()

