from copy import copy
from collections import Iterable
from six import binary_type, text_type
from h5py import Group, Dataset, RegionReference, Reference, special_dtype
import json
import h5py
import numpy as np
import warnings
import os

from ...query import FORMDataset
from ...array import Array
from ...utils import docval, getargs, popargs, call_docval_func
from ...data_utils import RegionSlicer, DataIO, AbstractDataChunkIterator

from ...spec import SpecWriter, SpecReader


class H5Dataset(FORMDataset):
    @docval({'name': 'dataset', 'type': (Dataset, Array), 'doc': 'the HDF5 file lazily evaluate'},
            {'name': 'io', 'type': 'HDF5IO', 'doc': 'the IO object that was used to read the underlying dataset'})
    def __init__(self, **kwargs):
        self.__io = popargs('io', kwargs)
        call_docval_func(super(H5Dataset, self).__init__, kwargs)

    @property
    def io(self):
        return self.__io

    @property
    def regionref(self):
        return self.dataset.regionref

    @property
    def ref(self):
        return self.dataset.ref


class H5TableDataset(H5Dataset):

    @docval({'name': 'dataset', 'type': (Dataset, Array), 'doc': 'the HDF5 file lazily evaluate'},
            {'name': 'io', 'type': 'HDF5IO', 'doc': 'the IO object that was used to read the underlying dataset'},
            {'name': 'types', 'type': (list, tuple),
             'doc': 'the IO object that was used to read the underlying dataset'})
    def __init__(self, **kwargs):
        types = popargs('types', kwargs)
        call_docval_func(super(H5TableDataset, self).__init__, kwargs)
        self.__refgetters = dict()
        for i, t in enumerate(types):
            if t is RegionReference:
                self.__refgetters[i] = self.__get_regref
            elif t is Reference:
                self.__refgetters[i] = self.__get_ref
        tmp = list()
        for i in range(len(self.dataset.dtype)):
            sub = self.dataset.dtype[i]
            if sub.metadata:
                if 'vlen' in sub.metadata:
                    t = sub.metadata['vlen']
                    if t is text_type:
                        tmp.append('utf')
                    elif t is binary_type:
                        tmp.append('ascii')
                elif 'ref' in sub.metadata:
                    t = sub.metadata['ref']
                    if t is Reference:
                        tmp.append('object')
                    elif t is RegionReference:
                        tmp.append('region')
            else:
                tmp.append(sub.type.__name__)
        self.__dtype = tmp

    @property
    def dtype(self):
        return self.__dtype

    def __getitem__(self, arg):
        rows = copy(super(H5TableDataset, self).__getitem__(arg))
        if isinstance(arg, int):
            self.__swap_refs(rows)
        else:
            for row in rows:
                self.__swap_refs(row)
        return rows

    def __swap_refs(self, row):
        for i in self.__refgetters:
            getref = self.__refgetters[i]
            row[i] = getref(row[i])

    def __get_ref(self, ref):
        return self.io.get_container(self.dataset.file[ref])

    def __get_regref(self, ref):
        obj = self.__get_ref(ref)
        return obj[ref]


class H5ReferenceDataset(H5Dataset):

    def __getitem__(self, arg):
        ref = super(H5ReferenceDataset, self).__getitem__(arg)
        return self.io.get_container(self.dataset.file[ref])

    @property
    def dtype(self):
        return 'object'


class H5RegionDataset(H5ReferenceDataset):

    def __getitem__(self, arg):
        obj = super(H5RegionDataset, self).__getitem__(arg)
        ref = self.dataset[arg]
        return obj[ref]

    @property
    def dtype(self):
        return 'region'


class H5SpecWriter(SpecWriter):

    __str_type = special_dtype(vlen=binary_type)

    @docval({'name': 'group', 'type': Group, 'doc': 'the HDF5 file to write specs to'})
    def __init__(self, **kwargs):
        self.__group = getargs('group', kwargs)

    @staticmethod
    def stringify(spec):
        '''
        Converts a spec into a JSON string to write to a dataset
        '''
        return json.dumps(spec, separators=(',', ':'))

    def __write(self, d, name):
        data = self.stringify(d)
        dset = self.__group.create_dataset(name, data=data, dtype=self.__str_type)
        return dset

    def write_spec(self, spec, path):
        return self.__write(spec, path)

    def write_namespace(self, namespace, path):
        return self.__write({'namespaces': [namespace]}, path)


class H5SpecReader(SpecReader):

    @docval({'name': 'group', 'type': Group, 'doc': 'the HDF5 file to read specs from'})
    def __init__(self, **kwargs):
        self.__group = getargs('group', kwargs)
        super_kwargs = {'source': "%s:%s" % (os.path.abspath(self.__group.file.name), self.__group.name)}
        call_docval_func(super(H5SpecReader, self).__init__, super_kwargs)

    def __read(self, path):
        s = self.__group[path][()]
        if isinstance(s, bytes):
            s = s.decode('UTF-8')
        d = json.loads(s)
        return d

    def read_spec(self, spec_path):
        return self.__read(spec_path)

    def read_namespace(self, ns_path):
        ret = self.__read(ns_path)
        ret = ret['namespaces']
        return ret


class H5RegionSlicer(RegionSlicer):

    @docval({'name': 'dataset', 'type': (Dataset, H5Dataset), 'doc': 'the HDF5 dataset to slice'},
            {'name': 'region', 'type': RegionReference, 'doc': 'the region reference to use to slice'})
    def __init__(self, **kwargs):
        self.__dataset = getargs('dataset', kwargs)
        self.__regref = getargs('region', kwargs)
        self.__len = self.__dataset.regionref.selection(self.__regref)[0]
        self.__region = None

    def __read_region(self):
        if self.__region is None:
            self.__region = self.__dataset[self.__regref]

    def __getitem__(self, idx):
        self.__read_region()
        return self.__region[idx]

    def __len__(self):
        return self.__len


class H5DataIO(DataIO):
    """
    Wrap data arrays for write via HDF5IO to customize I/O behavior, such as compression and chunking
    for data arrays.
    """

    @docval({'name': 'data',
             'type': (np.ndarray, list, tuple, h5py.Dataset, Iterable),
             'doc': 'the data to be written. NOTE: If an h5py.Dataset is used, all other settings but link_data' +
                    ' will be ignored as the dataset will either be linked to or copied as is in H5DataIO.'},
            {'name': 'maxshape',
             'type': tuple,
             'doc': 'Dataset will be resizable up to this shape (Tuple). Automatically enables chunking.' +
                    'Use None for the axes you want to be unlimited.',
             'default': None},
            {'name': 'chunks',
             'type': (bool, tuple),
             'doc': 'Chunk shape or True ti enable auto-chunking',
             'default': None},
            {'name': 'compression',
             'type': (str, bool),
             'doc': 'Compression strategy. If a bool is given, then gzip compression will be used by default.' +
                    'http://docs.h5py.org/en/latest/high/dataset.html#dataset-compression',
             'default': None},
            {'name': 'compression_opts',
             'type': int,
             'doc': 'Parameter for compression filter',
             'default': None},
            {'name': 'fillvalue',
             'type': None,
             'doc': 'Value to eb returned when reading uninitalized parts of the dataset',
             'default': None},
            {'name': 'shuffle',
             'type': bool,
             'doc': 'Enable shuffle I/O filter. http://docs.h5py.org/en/latest/high/dataset.html#dataset-shuffle',
             'default': None},
            {'name': 'fletcher32',
             'type': bool,
             'doc': 'Enable fletcher32 checksum. http://docs.h5py.org/en/latest/high/dataset.html#dataset-fletcher32',
             'default': None},
            {'name': 'link_data',
             'type': bool,
             'doc': 'If data is an h5py.Dataset should it be linked to or copied. NOTE: This parameter is only ' +
                    'allowed if data is an h5py.Dataset',
             'default': False}
            )
    def __init__(self, **kwargs):
        # Get the list of I/O options that user has passed in
        ioarg_names = [name for name in kwargs.keys() if name not in['data', 'link_data']]
        # Remove the ioargs from kwargs
        ioarg_values = [popargs(argname, kwargs) for argname in ioarg_names]
        # Consume link_data parameter
        self.__link_data = popargs('link_data', kwargs)
        # Check for possible collision with other parameters
        if not isinstance(getargs('data', kwargs), Dataset) and self.__link_data:
            self.__link_data = False
            warnings.warn('link_data parameter in H5DataIO will be ignored')
        # Call the super constructor and consume the data parameter
        call_docval_func(super(H5DataIO, self).__init__, kwargs)
        # Construct the dict with the io args, ignoring all options that were set to None
        self.__iosettings = {k: v for k, v in zip(ioarg_names, ioarg_values) if v is not None}
        # Set io_properties for DataChunkIterators
        if isinstance(self.data, AbstractDataChunkIterator):
            # Define the chunking options if the user has not set them explicitly.
            if 'chunks' not in self.__iosettings and self.data.recommended_chunk_shape() is not None:
                self.__iosettings['chunks'] = self.data.recommended_chunk_shape()
            # Define the maxshape of the data if not provided by the user
            if 'maxshape' not in self.__iosettings:
                self.__iosettings['maxshape'] = self.data.maxshape
        if 'compression' in self.__iosettings:
            if isinstance(self.__iosettings['compression'], bool):
                if self.__iosettings['compression']:
                    self.__iosettings['compression'] = 'gzip'
                else:
                    self.__iosettings.pop('compression', None)
                    if 'compression_opts' in self.__iosettings:
                        warnings.warn('Compression disabled by compression=False setting. ' +
                                      'compression_opts parameter will, therefore, be ignored.')
                        self.__iosettings.pop('compression_opts', None)
        if 'compression' in self.__iosettings:
            if self.__iosettings['compression'] != 'gzip':
                warnings.warn(str(self.__iosettings['compression']) + " compression may not be available" +
                              "on all installations of HDF5. Use of gzip is recommended to ensure portability of" +
                              "the generated HDF5 files.")
        # Check possible parameter collisions
        if isinstance(self.data, Dataset):
            for k in self.__iosettings.keys():
                warnings.warn("%s in H5DataIO will be ignored with H5DataIO.data being an HDF5 dataset" % k)

    @property
    def link_data(self):
        return self.__link_data

    @property
    def io_settings(self):
        return self.__iosettings
