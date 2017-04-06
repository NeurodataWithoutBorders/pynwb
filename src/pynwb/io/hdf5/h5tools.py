import posixpath as _posixpath
import copy as _copy
from collections import Iterable
import numpy as np
import h5py as _h5py

from pynwb.core import DataChunkIterator

SOFT_LINK = 0
HARD_LINK = 1
EXTERNAL_LINK = 2

def set_attributes(obj, attributes):
    for key, value in attributes.items():
        if any(isinstance(value, t) for t in (set, list, tuple)):
            tmp = tuple(value)
            if len(tmp) > 0:
                if isinstance(tmp[0], str):
                    max_len = max(len(s) for s in tmp)
                    dt = '|S%d' % max_len
                    value = np.array(tmp, dtype=dt)
            else:
                print('converting %s to an empty numpy array' % key)
                value = np.array(value)
        obj.attrs[key] = value

def write_group(parent, name, subgroups, datasets, attributes, links):
    group = parent.create_group(name)
    # write all groups
    if subgroups:
        for subgroup_name, builder in subgroups.items():
            # do not create an empty group without attributes or links
            tmp_links = write_group(group,
                            subgroup_name,
                            builder.groups,
                            builder.datasets,
                            builder.attributes,
                            builder.links)
    # write all datasets
    if datasets:
        for dset_name, builder in datasets.items():
            write_dataset(group,
                          dset_name,
                          builder.get('data'),
                          builder.get('attributes'))
    # write all links
    if links:
        for link_name, builder in links.items():
            write_link(group, name, builder.target)
    set_attributes(group, attributes)

def write_link(parent, name, target_builder):
    # get target path
    names = list()
    curr = target_builder
    while curr is not None:
        names.append(curr.name)
        curr = target_builder.parent
    delim = "/"
    path = "%s%s" % delim.join(reversed(names))
    # source will indicate target_builder's location
    if parent.file.filename == target_builder.source:
        link_obj = SoftLink(path)
    else:
        link_obj = ExternalLink(target_builder.source, path)
    parent[name] = link_obj

def __get_shape_helper(data):
    shape = list()
    if hasattr(data, '__len__'):
        shape.append(len(data))
        if len(data) and not isinstance(data[0], str):
            shape.extend(__get_shape_helper(data[0]))
    return tuple(shape)

def __get_shape(data):
    if hasattr(data, '__len__') and not isinstance(data, str):
        return __get_shape_helper(data)
    else:
        return None

def __get_type(data):
    if isinstance(data, str):
        return _h5py.special_dtype(vlen=bytes)
    elif not hasattr(data, '__len__'):
        return type(data)
    else:
        return __get_type(data[0])

def isintance_inmemory_array(data):
    """Check if an object is a common in-memory data structure"""
    return isinstance(data, list) or \
           isinstance(data, np.ndarray) or \
           isinstance(data, tuple) or \
           isinstance(data, set) or \
           isinstance(data, str) or \
           isinstance(data, frozenset)

def write_dataset(parent, name, data, attributes):
    """
    Write a dataset to HDF5.

    The function uses other dataset-dependent write functions, e.g,
    __scalar_fill__, __list_fill__ and __chunked_iter_fill__ to write the data.

    :param parent: Parent HDF5 object
    :param name: Name of the data to be written.
    :param data: Data object to be written.
    :param attributes:
    """
    dset = None
    if isinstance(data, str):
        dset = __scalar_fill__(parent, name, data)
    elif isinstance(data, DataChunkIterator):
        dset = __chunked_iter_fill__(parent, name, data)
    elif isinstance(data, Iterable) and not isintance_inmemory_array(data):
        dset = __chunked_iter_fill__(parent, name, DataChunkIterator(data=data, buffer_size=100))
    elif hasattr(data, '__len__'):
        dset = __list_fill__(parent, name, data)
    else:
        dset = __scalar_fill__(parent, name, data)
    set_attributes(dset, attributes)

def __extend_dataset__(dset):
    new_shape = list(dset.shape)
    new_shape[0] = 2*new_shape[0]
    dset.resize(new_shape)

def __trim_dataset__(dset, length):
    new_shape = list(dset.shape)
    new_shape[0] = length
    dset.resize(new_shape)

def __selection_max_bounds__(selection):
    """Determine the bounds of a numpy selection index tuple"""
    if isinstance(selection, int):
        return selection+1
    elif isinstance(selection, slice):
        return selection.stop
    elif isinstance(selection, list) or isinstance(selection, np.ndarray):
        return np.nonzero(selection)[0][-1]+1
    elif isinstance(selection, tuple):
        return tuple([__selection_max_bounds__(i) for i in selection])

def __scalar_fill__(parent, name, data):
    dtype = __get_type(data)
    dset = parent.create_dataset(name, data=data, shape=None, dtype=dtype)
    return dset

def __chunked_iter_fill__(parent, name, data):
    """
    Write data to a dataset one-chunk-at-a-time based on the given DataChunkIterator

    :param parent: The parent object to which the dataset should be added
    :type parent: h5py.Group, h5py.File
    :param name: The name of the dataset
    :type name: str
    :param data: The data to be written.
    :type data: DataChunkIterator

    """
    recommended_chunks = data.recommended_chunk_shape()
    chunks = True if recommended_chunks is None else recommended_chunks
    baseshape = data.recommended_data_shape()
    dset = parent.create_dataset(name, shape=baseshape, dtype=data.dtype, maxshape=data.max_shape, chunks=chunks)
    for chunk_i in data:
        # Determine the minimum array dimensions to fit the chunk selection
        max_bounds = __selection_max_bounds__(chunk_i.selection)
        if not hasattr(max_bounds, '__len__'):
            max_bounds = (max_bounds,)
        # Determine if we need to expand any of the data dimensions
        expand_dims = [i for i, v in enumerate(max_bounds) if v is not None and v > dset.shape[i]]
        # Expand the dataset if needed
        if len(expand_dims) > 0:
            new_shape = np.asarray(dset.shape)
            new_shape[expand_dims] = np.asarray(max_bounds)[expand_dims]
            dset.resize(new_shape)
        # Process and write the data
        dset[chunk_i.selection] = chunk_i.data
    return dset

def __list_fill__(parent, name, data):
    data_shape = __get_shape(data)
    data_dtype = __get_type(data)
    dset = parent.create_dataset(name, shape=data_shape, dtype=data_dtype)
    if len(data) > dset.shape[0]:
        new_shape = list(dset.shape)
        new_shape[0] = len(data)
        dset.resize(new_shape)
    dset[:] = data
    return dset
