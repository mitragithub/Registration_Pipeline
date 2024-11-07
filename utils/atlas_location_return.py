from importlib.machinery import SourceFileLoader
from glob import glob
from os.path import join
import numpy as np
from scipy.interpolate import interpn
import sys
emlddmm = SourceFileLoader("emlddmm","/nfs/data/main/M32/RegistrationData/Bin/EMLDDMM_Library/emlddmm.py").load_module()
import glymur


def atlas_location_from_registered_space_pixel(
    row, col,
    jp2_filename,
    pixel_size_row, pixel_size_col,
    location_of_first_row, location_of_first_col,
    transform_path,
    verbose=False,
):
    '''
    Return a triple (z,y,x) (ake slice,row,col order) for a point in
atlas space,
    when a user inputs a row,col location in pixel space from the viewer,
    with some auxilary file locations.


    Parameters
    ----------
    row: int (or could be float)
        The row of the pixel that the user clicked on in the viewer.
    col: int (or could be float)
        The column of the pixel that the user clicked on in the viewer.
    jp2_filename: str
        The name of the high resolution Nissl jp2 file being shown in
the viewer.
        This is used to get the name of the slice, which is necessary
to load the
        correct displacement field.
    pixel_size_row: float
        The size of a pixel in microns in the row direction for the
slice being displayed
        in the viewer.  In many cases this would be 0.56 microns.
    pixel_size_col: float
        The size of a pixel in microns in the col direction for the
slice being displayed
        in the viewer.  In many cases this would be 0.56 microns.
    location_of_first_row: float
        The location, in microns, of the first row.  For a typical
coronal mouse slice
        that is 18000x240000 pixels at 0.46 micron resolution, with
the origin in
        the middle, this would be -4139.77.
    location_of_first_col: float
        The location, in microns, of the first column.  For a typical
coronal mouse slice
        that is 18000x240000 pixels at 0.46 micron resolution, with
the origin in
        the middle, this would be -5519.77.
    verbose: bool
        If True, print out extra information while the function is
running.  Defaults
        to False.

    Raises
    ------
    Exception
        If we cannot find the displacement field, or if we find more
than one matching
        the key.

    Returns
    -------
    atlas_coordinate: list of float
        The corresponding coordinate in our atlas.
    atlas_name: str
        The name of our atlas, which is part of the displacement field filename.

    Note
    ----
    Pixel size and origin information should be read from a specific file in the
    future.  Xu would generate this file.  In this case the interface
should change
    to reading a filename.


    '''

     # step 1, convert from pixels to physical location
    if verbose: print(f'Location clicked {row},{col}')
    x0 = row*pixel_size_row + location_of_first_row
    x1 = col*pixel_size_col + location_of_first_col
    if verbose: print(f'Physical location {x0},{x1}')

    # step 2, get last 4 digits of jp2 filename
    key = jp2_filename[-8:-4]
    if verbose: print(f'The key for this slice is {key}')

    # step 3, find the vtk file with this key
    displacement_files =glob(join(transform_path,'*_'+key+'_to*displacement.vtk'))
    n_files = len(displacement_files)
    if n_files != 1:
        raise Exception(f'Expected only one displacement file, but found {n_files}')
    if verbose: print(f'Found displacement file {displacement_files[0]}')
    # step 4, load the vtk displacement
    xd,d,_,_ = emlddmm.read_data(displacement_files[0])
    d = d.squeeze() # squeeze out extra dimensions

    # step 5, get the atlas coordinate by interpolating the displacement
    atlas_coordinate =(interpn(xd[1:],d.transpose(1,2,0),(x0,x1),bounds_error=False,fill_value=None) + np.array([xd[0][0],x0,x1]))[0]
    if verbose: print(f'Found atlas coordinate {atlas_coordinate}')

    # step 6, get the name of the atlas
    to_ind = displacement_files[0].rfind('_to_')
    displacement_ind = displacement_files[0].rfind('_displacement')
    atlas_name = displacement_files[0][to_ind+4:displacement_ind]
    if verbose: print(f'Found atlas name {atlas_name}')

    # step 7, return
    return atlas_coordinate.tolist(), atlas_name


def main():
    row, col, jp2_filename, brain_id = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3], sys.argv[4]
    transform_path = glob(f'/nfs/data/main/*/RegistrationData/*/{brain_id}/*GDM*/registered_histology/atlas_to_registered_histology/transforms/')
    if len(transform_path) != 1:
        print('registration location not accurate')
    transform_path = transform_path[0]
    jp2meta = glymur.Jp2k(jp2_filename)
    imgheight, imgwidth= jp2meta.shape[0], jp2meta.shape[1]
    pixel_size_row, pixel_size_col = 0.46, 0.46
    location_of_first_row = -(imgheight//2) * pixel_size_row
    location_of_first_col = -(imgwidth//2) * pixel_size_col

    return atlas_location_from_registered_space_pixel(
        row, col,
        jp2_filename,
        pixel_size_row, pixel_size_col,
        location_of_first_row, location_of_first_col,
        transform_path,
        verbose=True,
        )       

if __name__ == "__main__":
    main()