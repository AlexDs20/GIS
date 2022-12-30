import os
import rasterio
import numpy as np
import laspy


data_dir = '../data/70_7/'
wbt_exe = 'whitebox_tools'
resolution = 2
current_folder = os.getcwd()
CRS = 'EPSG:3006'


def compute_veg_density(input, output):
    """
    - Remove ground points
    - Rasterize the counts of points
    """
    tmp_laz_file = os.path.splitext(output)[0]+'.laz'
    tmp_ground_count_raster = os.path.splitext(output)[0]+'_ground_count.tif'
    tmp_all_count_raster = os.path.splitext(output)[0]+'_all_count.tif'

    # Create data for "count"
    las = laspy.read(input)
    las.z = np.ones(las.z.shape)
    las.write(tmp_laz_file)

    # Rasterize count of ground points
    cmd = f"{wbt_exe} -r=LidarPointDensity \
        --input={tmp_laz_file} \
        --output={tmp_ground_count_raster} \
        --resolution={resolution} \
        --radius={2*resolution} \
        --exclude_cls='0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18' \
        "
    os.system(cmd)

    # Rasterize all points
    cmd = f"{wbt_exe} -r=LidarPointDensity \
        --input={tmp_laz_file} \
        --output={tmp_all_count_raster} \
        --resolution={resolution} \
        --radius={2*resolution} \
        "
    os.system(cmd)

    # Read both rasters and take ratio
    with rasterio.open(tmp_ground_count_raster) as ground_count:
        with rasterio.open(tmp_all_count_raster) as all_count:
            gc = ground_count.read().squeeze()
            ac = all_count.read().squeeze()
            meta = all_count.meta

    density = ac / gc
    density[gc==0] = ac.max() + 1

    with rasterio.open(output, 'w', **meta) as dst:
        dst.write(density, 1)

    os.remove(tmp_laz_file)
    os.remove(tmp_ground_count_raster)
    os.remove(tmp_all_count_raster)


def compute_gradients(input, output):
    with rasterio.open(input) as dataset:
        data = dataset.read().squeeze()
        meta = dataset.meta

    gradients = np.array(np.gradient(data, resolution))
    gradients = np.sqrt(np.sum(gradients**2, axis=0))

    with rasterio.open(output, 'w', **meta) as dst:
        dst.write(gradients, 1)
    return gradients


def main():
    """
    In practice, one wants to select ground points and compute the gradients as we create the grid.
    However, I don't know how to smartly go through the points.
    Instead, make use of whitebox tools:

        To find steepness:
            - Keep only ground points
            - Compute elevation grid
            - Compute gradients

        To find how dense forest is:
            - Remove ground points
            - Use segmentation algorithm to find trees
            - Each tree
                - Height
                - Width
            - Compute some sort of density estimate
    """
    os.chdir(data_dir)
    list_files = [f for f in os.listdir('.') if os.path.splitext(f)[-1] in ['.laz', '.las']]

    for file in list_files:
        print(file)

        # Compute a ground elevation map, high res
        out_file_hr = os.path.splitext(file)[0]+'_ground_points_hr.tif'
        # Keep only ground points
        cmd = f"{wbt_exe} -r=LidarTINGridding \
            --input={file} \
            --output={out_file_hr} \
            --resolution=0.5 \
            --exclude_cls='0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18'"
        os.system(cmd)

        out_file = os.path.splitext(file)[0]+'_ground_points_lr.tif'
        # Keep only ground points
        cmd = f"{wbt_exe} -r=LidarTINGridding \
            --input={file} \
            --output={out_file} \
            --resolution={resolution} \
            --exclude_cls='0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18'"
        os.system(cmd)

        # Compute gradients
        out_file_grad = os.path.splitext(file)[0]+'_ground_points_grad.tif'
        compute_gradients(out_file, out_file_grad)
        os.remove(out_file)

        # Do stuff to get vegetation "density"
        out_veg_file = os.path.splitext(file)[0]+'_veg_density.tif'
        compute_veg_density(file, out_veg_file)


if __name__ == '__main__':
    main()
