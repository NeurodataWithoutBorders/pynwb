# flake8: noqa: F401
from .container import Container, Data, DataRegion
from .utils import docval, getargs
from .data_utils import ListSlicer
from .backends.hdf5.h5_utils import H5RegionSlicer, H5Dataset


@docval({'name': 'dataset', 'type': None, 'doc': 'the HDF5 dataset to slice'},
        {'name': 'region', 'type': None, 'doc': 'the region reference to use to slice'},
        is_method=False)
def get_region_slicer(**kwargs):
    dataset, region = getargs('dataset', 'region', kwargs)
    if isinstance(dataset, (list, tuple, Data)):
        return ListSlicer(dataset, region)
    elif isinstance(dataset, H5Dataset):
        return H5RegionSlicer(dataset, region)
    return None
