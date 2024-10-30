# -*- coding: utf-8 -*-

import jsonontology_parse as jp
import SimpleITK as sitk
from skimage import measure
import numpy as np
import json
import os,sys
import scipy.misc
import cv2
import skimage
from functools import partial
from multiprocessing import Pool

imgloc='/nfs/data/main/M32/STP_RegistrationData/data/deformedAtlas/'
# namepattern = '%s_downsample_regANNO_50.img'  #'_annotation_raw.img'
namepattern = '%s_downsample_regANNO_10.img'  #'_annotation_raw.img'

outdir = '/nfs/data/main/M32/STP_RegistrationData/data/Json/'
outdir2 = '/nfs/data/main/M32/STP_RegistrationData/data/Json_support/'
def slice_image(pmdno, sliceno):
    img = load_image(imgloc +'/'+pmdno+ namepattern)
    imgslice = np.array(img[:,int(sliceno-1),:])
    return imgslice


def coordinate_change(pt,siz):
    height, width = siz
    pt_x = pt[0]/width * 11377  #8557
    pt_y = -pt[1]/height * 8557 #11377
    # pt_x = pt[0]
    # pt_y = -pt[1]
    return [pt_x, pt_y]

def getcomponents(imgslice):
    siz = imgslice.shape

    colors = np.union1d(np.array(imgslice).ravel(),np.array([]))
  
    json_data = """{"type":"FeatureCollection","features":["""
    unknown_colors = []
    
    for ci in colors[1:]: 
        count = True
        bwarr = imgslice==ci
        con = measure.find_contours(bwarr,0.5)
        #con = measure.subdivide_polygon(con, degree=2)
        sum_1 = 0
        (br_reg_name,depth) = jp.ontology_find(ci)

        if br_reg_name is None:
            br_reg_name = {'name': '##', 'acronym': '00'}
            unknown_colors.append(ci)
        mul_pol = []
        for coni in con:
            #print coni
            conxy = np.array(coni)
            index_x = np.argmin((conxy[:,1]))
            slope = (conxy[:,0][index_x+1]-conxy[:,0][index_x])/(conxy[:,1][index_x+1]-conxy[:,1][index_x]+0.00001)
            if slope < 0:
                x_coord = list(conxy[:,1])
                y_coord = list(conxy[:,0])
                temp_arr = []
                for j in range(len(x_coord)):
                    temp_arr.append(coordinate_change([x_coord[j],y_coord[j]], siz))

                if len(con)==1:
                    coord = """\n{"type":"Feature","id":"%d","properties":{"name":"%s","acronym": "%s" },"geometry":{"type":"Polygon","coordinates":["""%(ci,br_reg_name["name"], br_reg_name["acronym"])+str(temp_arr)+"""]}},"""
                    count = False

                else:
                    mul_pol.append(temp_arr)

        if count is True:
            coord = """\n{"type":"Feature","id":"%d","properties":{"name":"%s","acronym":"%s"},"geometry":{"type":"MultiPolygon","coordinates":["""%(ci,br_reg_name["name"], br_reg_name["acronym"])+str(mul_pol)+"""]}},"""

        json_data = json_data + coord

    return json_data[:-1] + "]}", set(unknown_colors)

def single(si, imgA):
    # imgA = sitk.GetArrayFromImage(img)
    # shape = img.GetSize()
    # ns = shape[2] # XXX
    unknown_cols = []

    # if sliceno is not None and si!=sliceno-1:
	#     continue
    if len(shape)==3:
        imgslice = imgA[si,:,:]  #XXX adding front pad
    else:
        imgslice = imgA[si,:,:,0] #XXX

    imgslice = np.rint(imgslice).astype(int)
    # imgslice = skimage.transform.resize(imgslice, (11377, 8557), order=0, preserve_range=True, anti_aliasing=True)
    # imgslice = np.asarray(imgslice, dtype='int64')

    # imgslice = np.rot90(imgslice,axes=(1, 0))
    imgslice=np.flip(imgslice, axis=1)
    cv2.imwrite(outdir2+'/HUA_'+pmdno+'/atlas_img_'+str(si+1)+'.tif', np.asarray(imgslice, dtype='uint16'))
    json_data, ukc = getcomponents(imgslice)
    if len(ukc)>0:
        print(si, ukc)
    unknown_cols = np.union1d(unknown_cols,list(ukc))
    file_json = open('%s/HUA_%s/atlas_%s_%d.json' % (outdir,pmdno,pmdno, si+1),'w')
    file_json.write(json_data)
    file_json.close()
    print(si)

if __name__ =="__main__":
    pmdno = sys.argv[1]
    pmdno = pmdno[0:6]
    sliceno = None
    if len(sys.argv)>2:
        sliceno = int(sys.argv[2])

    imgpath = imgloc+'/'+namepattern
    img = sitk.ReadImage(imgpath %(pmdno))
    shape = img.GetSize()
    ns = shape[2] # XXX
    img = sitk.GetArrayFromImage(img)

    if not os.path.exists(outdir+'/HUA_'+pmdno):
        os.mkdir(outdir+'/HUA_'+pmdno)
    if not os.path.exists(outdir2+'/HUA_'+pmdno):
        os.mkdir(outdir2+'/HUA_'+pmdno)

    p=Pool(8)
    p.map(partial(single, imgA=img), range(ns))
    # for si in range(ns):
        

