import os
import rasterio
import numpy as np


data_dir = '../data/70_7/'
tmp_dir = './tmp/'
wbt_exe = 'whitebox_tools'
resolution = 2
current_folder = os.getcwd()
CRS = 'EPSG:3006'

os.makedirs(tmp_dir, exist_ok=True)


def compute_gradients(input, output):
    with rasterio.open(input) as dataset:
        data = dataset.read().squeeze()
        meta = dataset.meta

    gradients = np.array(np.gradient(data, resolution))
    gradients = np.sqrt(np.sum(gradients*gradients, axis=0))

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
        out_file = os.path.splitext(file)[0]+'_ground_points.tif'
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


if __name__ == '__main__':
    main()
