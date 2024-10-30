
# coding: utf-8

# In[1]:


import sys
#sys.path.append("/cis/home/dtward/Documents/image_lddmm_tensorflow/")


import numpy as np # for arrays
#get_ipython().magic(u'matplotlib notebook')
import matplotlib as mpl # for graphics
import matplotlib.pyplot as plt
import nibabel as nib # for loading neuroimages
import lddmm # algorithm
import vis # visualization
import tensorflow as tf
import imp # use imp.reload to update modules during development
import basic_vtk_io as vtk
imp.reload(vtk)
import os
import warnings
import pickle
os.environ["CUDA_VISIBLE_DEVICES"]=""


# In[2]:

def main():
    filenames = os.listdir('/mnt/disk132/main/STP_RegistrationData/data/transfer_para/')
    for fname in filenames:
        convert_pickle(fname)


# In[3]:


def load_data(fname):
    with open(fname,'rb') as f:
        out = pickle.load(f)
    return out


# In[4]:


def convert_pickle(fname):
#fname = filenames[0]

    out = load_data(fname)



# In[6]:


    atlas_image_fname = '/mnt/disk132/main/STP_RegistrationData/ATLAS/average_template_50.vtk'
    x0I,x1I,x2I,I,title,names = vtk.read_vtk_image(atlas_image_fname)
    # convert to mm
    x0I /= 1000.0
    x1I /= 1000.0
    x2I /= 1000.0
    xI = [x0I,x1I,x2I]
    nxI = I.shape[:3]
    dxI = np.array([x0I[1]-x0I[0], x1I[1]-x1I[0], x2I[1]-x2I[0]])
    I = I.squeeze()


# In[20]:


# output directory, you must specify this
    output_directory = '/mnt/disk132/main/STP_RegistrationData/data/transfer_para/vtkoutput_'+fname.split('.')[0]
    if os.path.exists(output_directory):
        warnings.warn('output directory {} already exists'.format(output_directory))
    else:
        os.mkdir(output_directory)

    # note because we don't have the original images saved, I am hardcoding 50 micron
    dxI = np.array([0.05,0.05,0.05])
    xI = [ np.arange(out['vt0'].shape[i]) - np.mean(np.arange(out['vt0'].shape[0])) for i in range(3)]
    dxJ = np.array([0.05,0.05,0.05])
    xJ = [ np.arange(out['phiinvAinv0'].shape[i]) - np.mean(np.arange(out['phiinvAinv0'].shape[0])) for i in range(3)]


    # deformation of the atlas,
    X0I,X1I,X2I = np.meshgrid(*xI,indexing='ij')
    towrite = np.stack([out['Aphi0']-X0I,out['Aphi1']-X1I,out['Aphi2']-X2I],axis=-1)[:,:,:,:,None].astype(np.float32)
    vtk.write_vtk_image(xI[0],xI[1],xI[2], towrite,
                        os.path.join(output_directory,'atlas_to_registered_displacement.vtk'), 'atlas_to_registered')

    # now registered to atlas
    X0J,X1J,X2J = np.meshgrid(*xJ,indexing='ij')
    towrite = np.stack([out['phiinvAinv0']-X0J,out['phiinvAinv1']-X1J,out['phiinvAinv2']-X2J],axis=-1)[:,:,:,:,None].astype(np.float32)
    vtk.write_vtk_image(xJ[0],xJ[1],xJ[2], towrite,
                        os.path.join(output_directory,'registered_to_atlas.vtk'),
                        'registered_to_atlas')


    # we will save more data that is not required in BICCN format
    # now determinant of jacobian
    phix_x,phix_y,phix_z = np.gradient(out['phi0'],dxI[0],dxI[1],dxI[2]);
    phiy_x,phiy_y,phiy_z = np.gradient(out['phi1'],dxI[0],dxI[1],dxI[2]);
    phiz_x,phiz_y,phiz_z = np.gradient(out['phi2'],dxI[0],dxI[1],dxI[2]);
    detjac = (phix_x*(phiy_y*phiz_z - phiy_z*phiz_y)
        - phix_y*(phiy_x*phiz_z - phiy_z*phiz_x)
        + phix_z*(phiy_x*phiz_y - phiy_y*phiz_x))*np.linalg.det(out['A']);
    towrite = detjac[:,:,:,None,None].astype(np.float32)
    vtk.write_vtk_image(xI[0],xI[1],xI[2], towrite,
                        os.path.join(output_directory,'atlas_to_registered_detjac.vtk'),
                        'atlas_to_registered_detjac')

    # now velocity field
    towrite = np.stack([out['vt0'],out['vt1'],out['vt2']],axis=-2).astype(np.float32)
    vtk.write_vtk_image(xI[0],xI[1],xI[2], towrite,
                        os.path.join(output_directory,'atlas_to_registered_velocity.vtk'),
                        'atlas_to_registered_velocity')

    # for completeness save the affine matrix A
    with open(os.path.join(output_directory,'atlas_to_registered_affine.txt'),'wt') as f:
        for i in range(4):
            for j in range(4):
                f.write(str(out['A'][i,j]))
                f.write(' ')
            f.write('\n')

if __name__== "__main__":
    main()
