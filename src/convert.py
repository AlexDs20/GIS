from collections import OrderedDict
import numpy as np
import rasterio
from rasterio.enums import Resampling


from pprint import pprint


def list_available_bands(file: str):
    """ List the available bands at the different resolutions
    """
    with rasterio.open(file) as sat:
        subdatasets = sat.subdatasets

    for subdataset in subdatasets:
        with rasterio.open(subdataset) as bands:
            print(f'At resolution {bands.res}, with data type {set(bands.dtypes)}: ')
            for description in bands.descriptions:
                print('\t', description)


def compute_index(file: str, index: str, out_file: str=None):
    """ Use the satellite file to compute index
    """
    pass


def get_bands_in_dataset(file: str, bands: list) -> OrderedDict:
    """ return the bands location from the file

    Go through the file subdatasets and check for the bands.
    Returns a mapping between the band and it's subdataset and band in that subdataset as well as the band resolution
    {'BAND': [INT_SUBDATASET, INT_BAND_IDX, TUPLE_RESOLUTION]}
    """
    with rasterio.open(file) as sat:
        subdatasets = sat.subdatasets

    bands_mapping = OrderedDict()

    for band in bands:
        # Go through subdatasets (grouped by resolution)
        for i, subdataset in enumerate(subdatasets):
            with rasterio.open(subdataset) as datasets:
                res = datasets.res
                # Go through the description of each band of the dataset, 1 at a time
                for j, description in enumerate(datasets.descriptions):
                    # If of interest
                    if band in description:
                        if band not in bands_mapping:
                            bands_mapping[band] = [i, j, res]
                        elif band in bands_mapping and abs(bands_mapping[band][-1][0]) > abs(res[0]):
                            bands_mapping[band] = [i, j, res]

    return bands_mapping


def resample_bands(
    file: str,
    out_file: str,
    bands: list=['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B10','B11','B12'],
    resample_to_band: str='B4',
    algorithm: str=''):
    """ Save tif file of the bands at the same resolution

    1: find the band to use as a reference to which to resample to.
    2: Go through all the bands we want to keep and resample to the reference band
    """

    mapping = get_bands_in_dataset(file, bands)

    pprint(mapping)
    with rasterio.open(file) as sat:
        subdatasets = sat.subdatasets

    # Read the reference band
    with rasterio.open(subdatasets[mapping[resample_to_band][0]]) as datasets:
        meta = datasets.meta

    pprint(meta)

    # DATA = np.empty((len(mapping), meta['height'], meta['width']), dtype=meta['dtype'])

    # # Read all the other bands
    # for i, (band, [sub, b, res]) in enumerate(mapping.items()):
    #     with rasterio.open(subdatasets[sub]) as datasets:
    #         DATA[i] = datasets.read(
    #             b+1,
    #             out_shape=(1, meta['height'], meta['width']),
    #             resampling=Resampling.nearest)
    #         print(i, band)


def main(file: str, out_file: str='./out.tif') -> None:
    list_available_bands(file)

    # resample_bands(file, out_file)

    # for subdataset in subdatasets:
    #     with rasterio.open(subdataset) as band:
    #         pprint(band.profile)
    #         pprint(band.read())


if __name__ == '__main__':
    file = '/home/alexandre/Downloads/S2B_MSIL2A_20230626T103629_N0509_R008_T33WWQ_20230626T120541.zip'

    main(file)
