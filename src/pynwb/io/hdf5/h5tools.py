__all__ = [
    'GroupBuilder',
    'DatasetBuilder',
    'LinkBuilder',
]

import itertools as _itertools
import posixpath as _posixpath
import copy as _copy
from collections import Iterable, Callable
import numpy as np
import h5py as _h5py

from pynwb.core import docval, getargs

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
    links_to_create = _copy.deepcopy(links)
    if subgroups:
        for subgroup_name, builder in subgroups.items():
            # do not create an empty group without attributes or links
            #if builder.is_empty():
            #    continue
            tmp_links = write_group(group,
                            subgroup_name,
                            builder.groups,
                            builder.datasets,
                            builder.attributes,
                            builder.links)
            #for link_name, target in tmp_links.items():
            #    if link_name[0] != '/':
            #        link_name = _posixpath.join(name, link_name)
            #    links_to_create[link_name] = target
            links_to_create.update(tmp_links)
    if datasets:
        for dset_name, builder in datasets.items():
            write_dataset(group,
                          dset_name,
                          builder.get('data'),
                          builder.get('attributes'))

    set_attributes(group, attributes)

    return {_posixpath.join(name, k) if k[0] != '/' else k: v
            for k, v in links_to_create.items()}



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

def write_dataset(parent, name, data, attributes, function=None):
    dset = None
    if isinstance(data, str):
        dset = __scalar_fill__(parent, name, data)
    elif hasattr(data, '__len__'):
        dset = __list_fill__(parent, name, data)
    elif isinstance(data, Iterable):
        chunk_size = 100
        #TODO: do something to figure out appropriate chunk_size
        dset = __iter_fill__(parent, name, data, chunk_size, function=None)
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

def __scalar_fill__(parent, name, data):
    dtype = __get_type(data)
    dset = parent.create_dataset(name, data=data, shape=None, dtype=dtype)
    return dset

def __iter_fill__(parent, name, data, chunk_size, function=None):
    #data_shape = list(__get_shape(data))
    #data_shape[0] = None
    #data_shape = tuple(data_shape)
    data_iter = iter(data)
    curr_chunk = [next(data_iter) for i in range(chunk_size)]

    data_shape = __get_shape(curr_chunk)
    data_dtype = __get_type(curr_chunk)
    max_shape = list(data_shape)
    max_shape[0] = None
    dset = parent.create_dataset(name, shape=data_shape, dtype=data_dtype, maxshape=max_shape)

    idx = 0
    more_data = True
    args = [data_iter] * chunk_size
    chunks = _itertools.zip_longest(*args, fillvalue=None)

    if function:
        def proc_chunk(chunk):
            dset[idx:idx+len(chunk),] = chunk
            function(chunk)
    else:
        def proc_chunk(chunk):
            dset[idx:idx+len(chunk),] = chunk

    while more_data:
        try:
            next_chunk = next(chunks)
        except StopIteration:
            curr_chunk = list(filter(lambda x: x, curr_chunk))
            more_data = False
        if idx >= dset.shape[0] or idx+len(curr_chunk) > dset.shape[0]:
            __extend_dataset__(dset)
        #dset[idx:idx+len(curr_chunk),] = curr_chunk
        proc_chunk(curr_chunk)
        curr_chunk = next_chunk
        idx += chunk_size
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
