from pynwb.core import docval, getargs
import numpy as np
import posixpath as _posixpath
import copy as _copy
import itertools as _itertools

from pynwb.spec import DatasetSpec, GroupSpec

from collections import Iterable


class GroupBuilder(dict):
    __link = 'links'
    __group = 'groups'
    __dataset = 'datasets'
    __attribute = 'attributes'

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group'},
            {'name': 'groups', 'type': dict, 'doc': 'a dictionary of subgroups to create in this group',
             'default': dict()},
            {'name': 'datasets', 'type': dict, 'doc': 'a dictionary of datasets to create in this group',
             'default': dict()},
            {'name': 'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this group',
             'default': dict()},
            {'name': 'links', 'type': dict, 'doc': 'a dictionary of links to create in this group',
             'default': dict()})
    def __init__(self, **kwargs):
        """
        Create a GroupBuilder object
        """
        super().__init__()
        super().__setitem__(GroupBuilder.__group, dict())
        super().__setitem__(GroupBuilder.__dataset, dict())
        super().__setitem__(GroupBuilder.__attribute, dict())
        super().__setitem__(GroupBuilder.__link, dict())
        self.obj_type = dict()
        name, groups, datasets, links, attributes = getargs('name', 'groups', 'datasets', 'links', 'attributes', kwargs)
        self.__name = name
        for name, group in groups.items():
            self.set_group(name, group)
        for name, dataset in datasets.items():
            self.set_dataset(name, dataset)
        for name, link in links.items():
            self.set_link(name, link)
        for name, val in attributes.items():
            self.set_attribute(name, val)

    @property
    def groups(self):
        return super().__getitem__(GroupBuilder.__group)

    @property
    def datasets(self):
        return super().__getitem__(GroupBuilder.__dataset)

    @property
    def attributes(self):
        return super().__getitem__(GroupBuilder.__attribute)

    @property
    def links(self):
        return super().__getitem__(GroupBuilder.__link)

    @property
    def name(self):
        '''
        The name of this group
        '''
        return self.__name

    def __set_builder(self, builder, obj_type):
        name = builder.name
        if name in self.obj_type:
            if self.obj_type[name] != obj_type:
                raise KeyError("'%s' already exists as %s" % (name, self.obj_type[name]))
        super().__getitem__(obj_type)[name] = builder
        self.obj_type[name] = obj_type

    @docval({'name':'name', 'type': str, 'doc': 'the name of this dataset'},
            {'name':'data', 'type': None, 'doc': 'a dictionary of datasets to create in this dataset', 'default': None},
            {'name':'dtype', 'type': (type, np.dtype), 'doc': 'the datatype of this dataset', 'default': None},
            {'name':'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this dataset', 'default': dict()},
            {'name':'maxshape', 'type': (int, tuple), 'doc': 'the shape of this dataset. Use None for scalars', 'default': None},
            {'name':'chunks', 'type': bool, 'doc': 'whether or not to chunk this dataset', 'default': False},
            returns='the DatasetBuilder object for the dataset', rtype='DatasetBuilder')
    def add_dataset(self, **kwargs):
        """
        Create a dataset and add it to this group
        """
        name = kwargs.pop('name')
        builder = DatasetBuilder(name, **kwargs)
        self.set_dataset(builder)
        return builder

    @docval({'name': 'builder', 'type': 'DatasetBuilder', 'doc': 'the DatasetBuilder that represents this dataset'})
    def set_dataset(self, **kwargs):
        """
        Add a dataset to this group
        """
        builder, = getargs('builder', kwargs)
        self.__set_builder(builder, GroupBuilder.__dataset)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this subgroup'},
            {'name': 'groups', 'type': dict, 'doc': 'a dictionary of subgroups to create in this subgroup', 'default': dict()},
            {'name': 'datasets', 'type': dict, 'doc': 'a dictionary of datasets to create in this subgroup', 'default': dict()},
            {'name': 'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this subgroup', 'default': dict()},
            {'name': 'links', 'type': dict, 'doc': 'a dictionary of links to create in this subgroup', 'default': dict()},
            returns='the GroupBuilder object for the subgroup', rtype='GroupBuilder')
    def add_group(self, **kwargs):
        """
        Add a subgroup with the given data to this group
        """
        name = kwargs.pop('name')
        builder = GroupBuilder(name, **kwargs)
        self.set_group(name, builder)
        return builder

    @docval({'name': 'builder', 'type': 'GroupBuilder', 'doc': 'the GroupBuilder that represents this subgroup'})
    def set_group(self, **kwargs):
        """
        Add a subgroup to this group
        """
        name, builder, = getargs('name', 'builder', kwargs)
        self.__set_builder(name, builder, GroupBuilder.__group)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this link'},
            {'name': 'path', 'type': str, 'doc': 'the path within this HDF5 file'},
            returns='the builder object for the soft link', rtype='LinkBuilder')
    def add_link(self, **kwargs):
        """
        Create a soft link and add it to this group.
        """
        name, path = getargs('name', 'path', kwargs)
        builder = LinkBuilder(name, path)
        self.set_link(builder)
        return builder

    @docval({'name':'name', 'type': str, 'doc': 'the name of this link'},
            {'name':'file_path', 'type': str, 'doc': 'the file path of this external link'},
            {'name':'path', 'type': str, 'doc': 'the absolute path within the external HDF5 file'},
            returns='the builder object for the external link', rtype='ExternalLinkBuilder')
    def add_external_link(self, **kwargs):
        """
        Create an external link and add it to this group.
        """
        name, file_path, path = getargs('name', 'file_path', 'path', kwargs)
        builder = ExternalLinkBuilder(name, path, file_path)
        self.set_link(builder)
        return builder

    @docval({'name':'builder', 'type': 'LinkBuilder', 'doc': 'the LinkBuilder that represents this link'})
    def set_link(self, **kwargs):
        """
        Add a link to this group
        """
        builder = getargs('builder', kwargs)
        self.__set_builder(builder, GroupBuilder.__link)

    @docval({'name':'name', 'type': str, 'doc': 'the name of the attribute'},
            {'name':'value', 'type': None, 'doc': 'the attribute value'})
    def set_attribute(self, **kwargs):
        """
        Set an attribute for this group.
        """
        name, value = getargs('name', 'value', kwargs)
        super().__getitem__(GroupBuilder.__attribute)[name] = value
        self.obj_type[name] = GroupBuilder.__attribute

    #TODO: write unittests for this method
    def deep_update(self, builder):
        """ recursively update groups"""
        # merge subgroups
        groups = super(GroupBuilder, builder).__getitem__(GroupBuilder.__group)
        self_groups = super().__getitem__(GroupBuilder.__group)
        for name, subgroup in groups.items():
            if name in self_groups:
                self_groups[name].deep_update(subgroup)
            else:
                self.set_group(name, subgroup)
        # merge datasets
        datasets = super(GroupBuilder, builder).__getitem__(GroupBuilder.__dataset)
        self_datasets = super().__getitem__(GroupBuilder.__dataset)
        for name, dataset in datasets.items():
            #self.add_dataset(name, dataset)
            if name in self_datasets:
                self_datasets[name].deep_update(dataset)
                #super().__getitem__(GroupBuilder.__dataset)[name] = dataset
            else:
                self.set_dataset(name, dataset)
        # merge attributes
        for name, value in super(GroupBuilder, builder).__getitem__(GroupBuilder.__attribute).items():
            self.set_attribute(name, value)
        # merge links
        for name, link in super(GroupBuilder, builder).__getitem__(GroupBuilder.__link).items():
            self.set_link(name, link)

    def is_empty(self):
        """Returns true if there are no datasets, attributes, links or
           subgroups that contain datasets, attributes or links. False otherwise.
        """
        if (len(super().__getitem__(GroupBuilder.__dataset)) or
            len(super().__getitem__(GroupBuilder.__attribute)) or
            len(super().__getitem__(GroupBuilder.__link))):
            return False
        elif len(super().__getitem__(GroupBuilder.__group)):
            return all(g.is_empty() for g in super().__getitem__(GroupBuilder.__group).values())
        else:
            return True

    def __getitem__(self, key):
        """Like dict.__getitem__, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            raise KeyError(key)

    def get(self, key, default=None):
        """Like dict.get, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            return default

    def __get_rec(self, key_ar):
        # recursive helper for __getitem__
        if len(key_ar) == 1:
            return super().__getitem__(self.obj_type[key_ar[0]])[key_ar[0]]
        else:
            if key_ar[0] in super().__getitem__(GroupBuilder.__group):
                return super().__getitem__(GroupBuilder.__group)[key_ar[0]].__get_rec(key_ar[1:])
        raise KeyError(key_ar[0])


    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

    def __contains__(self, item):
        return self.obj_type.__contains__(item)

    def items(self):
        """Like dict.items, but iterates over key-value pairs in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).items(),
                                super().__getitem__(GroupBuilder.__dataset).items(),
                                super().__getitem__(GroupBuilder.__attribute).items(),
                                super().__getitem__(GroupBuilder.__link).items())

    def keys(self):
        """Like dict.keys, but iterates over keys in groups, datasets,
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).keys(),
                                super().__getitem__(GroupBuilder.__dataset).keys(),
                                super().__getitem__(GroupBuilder.__attribute).keys(),
                                super().__getitem__(GroupBuilder.__link).keys())

    def values(self):
        """Like dict.values, but iterates over values in groups, datasets,
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).values(),
                                super().__getitem__(GroupBuilder.__dataset).values(),
                                super().__getitem__(GroupBuilder.__attribute).values(),
                                super().__getitem__(GroupBuilder.__link).values())

class LinkBuilder(dict):
    def __init__(self, name, path):
        super().__init__()
        self['name'] = name
        self['path'] = path

    @property
    def path(self):
        return self['path']


class ExternalLinkBuilder(LinkBuilder):
    def __init__(self, name, path, file_path):
        super().__init__(name, path)
        self['file_path'] = file_path

    @property
    def file_path(self):
        return self['file_path']

class DatasetBuilder(dict):
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset'},
            {'name': 'data', 'type': None, 'doc': 'a dictionary of datasets to create in this dataset', 'default': None},
            {'name': 'dtype', 'type': (type, np.dtype), 'doc': 'the datatype of this dataset', 'default': None},
            {'name': 'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this dataset', 'default': dict()},
            {'name': 'maxshape', 'type': (int, tuple), 'doc': 'the shape of this dataset. Use None for scalars', 'default': None},
            {'name': 'chunks', 'type': bool, 'doc': 'whether or not to chunk this dataset', 'default': False})
    def __init__(self, **kwargs):
        '''
        Create a Builder object for a dataset
        '''
        super(DatasetBuilder, self).__init__()
        name, data, dtype, attributes, maxshape, chunks = getargs('name', 'data', 'dtype', 'attributes', 'maxshape', 'chunks', kwargs)
        self['data'] = data
        self['attributes'] = _copy.deepcopy(attributes)
        self.chunks = chunks
        self.maxshape = maxshape
        self.dtype = dtype
        self.__name = name

    @property
    def data(self):
        '''The data stored in the dataset represented by this builder'''
        return self['data']

    #@data.setter
    #def data(self, val):
    #    self['data'] = val

    @property
    def name(self):
        '''
        The name of this dataset
        '''
        return self.__name

    @property
    def attributes(self):
        '''The attributes on the dataset represented by this builder'''
        return self['attributes']

    @docval({'name':'name', 'type': str, 'doc': 'the name of the attribute'},
            {'name':'value', 'type': None, 'doc': 'the attribute value'})
    def set_attribute(self, **kwargs):
        name, value = getargs('name', 'value', kwargs)
        self['attributes'][name] = value

    @docval({'name':'dataset', 'type': 'DatasetBuilder', 'doc': 'the DatasetBuilder to merge into this DatasetBuilder'})
    def deep_update(self, **kwargs):
        """Merge data and attributes from given DatasetBuilder into this DatasetBuilder"""
        dataset = getargs('dataset', kwargs)
        if dataset.data:
            self['data'] = dataset.data #TODO: figure out if we want to add a check for overwrite
        self['attributes'].update(dataset.attributes)

    # XXX: leave this here for now, we might want it later
    #def __setitem__(self, args, val):
    #    raise NotImplementedError('__setitem__')

class DataChunkIterator(object):
    """Custom iterator class used to iterate over chunks of data.

    Derived classes must ensure that self.shape and self.dtype are set properly.
    define the self.max_shape property describing the maximum shape of the array.
    In addition, derived classes must implement the __next__ method (or overwrite _read_next_chunk
    if the default behavior of __next__ should be reused). The __next__ method must return
    in each iteration 1) a numpy array with the data values for the chunk and 2) a numpy-compliant index tuple
    describing where the chunk is located within the complete data.  HINT: numpy.s_ provides a
    convenient way to generate index tuples using standard array slicing. There are
    a number of additional functions that one can overwrite to customize behavior, e.g,
    the recommended_chunk_size() or recommended_

    The default implementation accepts any iterable and assumes that we iterate over
    the first dimension of the data array. The default implemention supports buffered read,
    i.e., multiple values from the input iterator can be combined to a single chunk. This is
    useful for buffered I/O operations, e.g., to improve performance by accumulating data
    in memory and writing larger blocks at once.
    """
    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'max_shape', 'type': tuple,
             'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions',
             'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def __init__(self, **kwargs):
        """Initalize the DataChunkIterator"""
        # Get the user parameters
        self.data, self.max_shape, self.dtype, self.buffer_size = getargs('data',
                                                                          'max_shape',
                                                                          'dtype',
                                                                          'buffer_size',
                                                                          kwargs)
        # Create an iterator for the data if possible
        self.__data_iter = iter(self.data) if isinstance(self.data, Iterable) else None
        self.__next_chunk = None
        self.__next_chunk_location = None
        self.__first_chunk_shape = None
        # Determine the shape of the data if possible
        if self.max_shape is None:
            # If the self.data object identifies it shape then use it
            if hasattr(self.data,  "shape"):
                self.max_shape = self.data.shape
                # Avoid the special case of scalar values by making them into a 1D numpy array
                if len(self.max_shape) == 0:
                    self.data = np.asarray([self.data, ])
                    self.max_shape = self.data.shape
                    self.__data_iter = iter(self.data)
            # Try to get an accurate idea of max_shape for other Python datastructures if possible.
            # Don't just call __get_shape for a generator as that would potentially trigger loading of all the data
            elif isinstance(self.data, list) or isinstance(self.data, tuple):
                self.max_shape = self.__get_shape(self.data)

        # If we have a data iterator, then read the first chunk
        if self.__data_iter is not None: # and(self.max_shape is None or self.dtype is None):
            self._read_next_chunk()

        # If we still don't know the shape then try to determine the shape from the first chunk
        if self.max_shape is None and self.__next_chunk is not None:
            data_shape = self.__get_shape(self.__next_chunk)
            self.max_shape = list(data_shape)
            self.max_shape[0] = None
            self.max_shape = tuple(self.max_shape)

        # Determine the type of the data if possible
        if self.__next_chunk is not None:
            self.dtype = self.__next_chunk.dtype
            self.__first_chunk_shape = self.__next_chunk.shape

    def __iter__(self):
        """Return the iterator object"""
        return self

    def _read_next_chunk(self):
        """Read a single chunk from self.__data_iter and store the results in
           self.__next_chunk and self.__chunk_location"""
        if self.__data_iter is not None:
            self.__next_chunk = []
            for i in range(self.buffer_size):
                try:
                    self.__next_chunk.append(next(self.__data_iter))
                except StopIteration:
                    pass
            next_chunk_size = len(self.__next_chunk)
            if next_chunk_size == 0:
                self.__next_chunk = None
                self.__next_chunk_location = None
            else:
                self.__next_chunk = np.asarray(self.__next_chunk)
                if self.__next_chunk_location is None:
                    self.__next_chunk_location = slice(0, next_chunk_size)
                else:
                    self.__next_chunk_location = slice(self.__next_chunk_location.stop,
                                                       self.__next_chunk_location.stop+next_chunk_size)
        else:
            self.__next_chunk = None
            self.__next_chunk_location = None

        return self.__next_chunk, self.__next_chunk_location

    @docval(returns="The following two items must be returned: \n" +
                    "* Numpy array (or scalar) with the data for the next chunk \n" +
                    "* Numpy-compliant index tuple describing the location of the chunk in the complete array. " +
                    "HINT: numpy.s_ provides a convenient way to generate index tuples using standard array slicing.")
    def __next__(self):
        """Return the next data chunk or raise a StopIteration exception if all chunks have been retrieved."""
        # If we have not already read the next chunk, then read it now
        if self.__next_chunk is None:
            self._read_next_chunk()
        # If we do not have any next chunk
        if self.__next_chunk is None:
            raise StopIteration
        # If this is the first time we see a chunk then remember the size of the first chunk
        if self.__first_chunk_shape is None:
            self.__first_chunk_shape = self.__next_chunk.shape
        # Keep the next chunk we need to return
        curr_chunk = self.__next_chunk
        curr_location = self.__next_chunk_location
        # Remove the next chunk from our list since we are returning it here. This avoids having 2 chunks in memory
        self.__next_chunk = None
        # Return the current next chunk
        return curr_chunk, curr_location

    @staticmethod
    def __get_shape(data):
        """Internal helper function used to determin the shape of data objects"""
        def __get_shape_helper(local_data):
            shape = list()
            if hasattr(local_data, '__len__'):
                shape.append(len(local_data))
                if len(local_data) and not isinstance(local_data[0], str):
                    shape.extend(__get_shape_helper(local_data[0]))
            return tuple(shape)
        if hasattr(data, 'shape'):
            return data.shape
        if hasattr(data, '__len__') and not isinstance(data, str):
            return __get_shape_helper(data)
        else:
            return None

    @docval(returns='Tuple with the recommended chunk shape or None if no particular shape is recommended.')
    def recommended_chunk_shape(self):
        """Recommend a chunk shape.

        To optimize iterative write the chunk should be aligned with the common shape of chunks returned by __next__
        or if those chunks are too large, then a well-aligned subset of those chunks. This may also be
        any other value in case one wants to recommend chunk shapes to optimize read rather
        than write. The default implementation returns None, indicating no preferential chunking option."""
        return None

    @docval(returns='Recommended initial shape for the full data. This should be the shape of the full dataset' +
                    'if known beforehand or alternatively the minimum shape of the dataset. Return None if no ' +
                    'recommendation is available')
    def recommended_data_shape(self):
        """Recommend an initial shape of the data. This is useful when progressively writing data and
        we want to recommend and initial size for the dataset"""
        if self.max_shape is not None:
            if np.all([i is not None for i in self.max_shape]):
                return self.max_shape
        return self.__first_chunk_shape


@docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'the parent spec to search'},
        {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to get the sub-specification for'},
        is_method=False)
def get_subspec(**kwargs):
    '''
    Get the specification from this spec that corresponds to the given builder
    '''
    spec, builder = getargs('spec', 'builder', kwargs)
    if isinstance(builder, DatasetBuilder):
        subspec = spec.get_dataset(builder.name)
    else:
        subspec = spec.get_group(builder.name)
    if subspec is None:
        ndt = builder.attributes.get('neurodata_type')
        if ndt is not None:
            subspec = spec.get_neurodata_type(ndt)
    return subspec

