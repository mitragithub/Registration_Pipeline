import numpy as np
import SimpleITK as sitk
import sys

dimension = 3
vectorComponentType = sitk.sitkFloat32
vectorType = sitk.sitkVectorFloat32
affine = sitk.AffineTransform(dimension)
identityAffine = list(affine.GetParameters())
identityDirection = list(affine.GetMatrix())
zeroOrigin = [0]*dimension
zeroIndex = [0]*dimension


# apply a displacement field
def fieldTransform(coordinate, field):
    myfieldcopy = sitk.Image(field)
    mytransform = sitk.DisplacementFieldTransform(dimension)
    mytransform.SetDisplacementField(myfieldcopy)
    return mytransform.TransformPoint(coordinate)

# apply an affine transform
def affineTransform(coordinate, params):
    mytransform = sitk.AffineTransform(dimension)
    mytransform.SetMatrix(params[0:9])
    mytransform.SetTranslation(params[9:12])
    mytransform.SetCenter(params[12:15])
    newcoordinate = mytransform.TransformPoint(coordinate)
    return newcoordinate

def horizontalTransform(coordinate, params):
    params3d = list([params[0],0,params[1],0,1,0,params[2],0,params[3],params[4],0,params[5],params[6],0,params[7]])
    mytransform = sitk.Euler3DTransform()
    mytransform.SetMatrix(params[0:9])
    mytransform.SetTranslation(params[9:12])
    mytransform.SetCenter(params[12:15])
    newcoordinate = mytransform.TransformPoint(coordinate)
    return newcoordinate

def main():
    horizontalfile = sys.argv[1]
    affinefile = sys.argv[2]
    fieldfile = sys.argv[3]
    atlasfile = sys.argv[4]
    targetfile = sys.argv[5]
    outputfilename = sys.argv[6]
    
    # load atlas
    atlas = sitk.ReadImage(atlasfile)
    target = sitk.ReadImage(targetfile)
    
    # load horizontal alignment transform
    #horizontaleulerlist = list(np.loadtxt(horizontalfile))
    with open(horizontalfile) as f:
        content = f.readlines()
    
    content = [x.strip() for x in content]
    contentline = content[0].split(',')
    params = [float(x) for x in contentline]
    params3d = list([params[0],0,params[1],0,1,0,params[2],0,params[3],params[4],0,params[5],params[6],0,params[7]])
    mytransform1 = sitk.Euler3DTransform()
    mytransform1.SetMatrix(params3d[0:9],tolerance=1e-5)
    mytransform1.SetTranslation(params3d[9:12])
    mytransform1.SetCenter(params3d[12:15])
    
    # load forward field 
    field = sitk.ReadImage(fieldfile,sitk.sitkVectorFloat64)
    mytransform2 = sitk.DisplacementFieldTransform(dimension)
    mytransform2.SetDisplacementField(field)
    
    # load affine transform list
    globalaffinelist = list(np.loadtxt(affinefile))
    params = list(globalaffinelist)
    mytransform3 = sitk.AffineTransform(dimension)
    mytransform3.SetMatrix(params[0:9])
    mytransform3.SetTranslation(params[9:12])
    mytransform3.SetCenter((4.15,7.3,5.5))
    
    # make composite transform
    composite_transform = sitk.Transform(3,sitk.sitkComposite)
    composite_transform.AddTransform(mytransform3)
    composite_transform.AddTransform(mytransform2)
    composite_transform.AddTransform(mytransform1)
    
    # apply transform to image
    outImg = sitk.Resample(atlas, target.GetSize(), mytransform3, sitk.sitkNearestNeighbor, (0,0,0), atlas.GetSpacing(), identityDirection, 0)
    outImg = sitk.Resample(outImg, target.GetSize(), mytransform2, sitk.sitkNearestNeighbor, (0,0,0), atlas.GetSpacing(), identityDirection, 0)
    outImg = sitk.Resample(outImg, target.GetSize(), mytransform1, sitk.sitkNearestNeighbor, (0,0,0), atlas.GetSpacing(), identityDirection, 0)
    sitk.WriteImage(outImg, outputfilename)
    return


if __name__ == "__main__":
    main()

