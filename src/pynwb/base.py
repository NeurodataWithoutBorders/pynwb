from warnings import warn
from collections.abc import Iterable

from hdmf.utils import docval, getargs, popargs, call_docval_func, get_docval
from hdmf.data_utils import extend_data
from hdmf.common import DynamicTable, VectorData
import numpy as np


from . import register_class, CORE_NAMESPACE
from .core import NWBDataInterface, MultiContainerInterface, NWBData


@register_class('ProcessingModule', CORE_NAMESPACE)
class ProcessingModule(MultiContainerInterface):
    """ Processing module. This is a container for one or more containers
        that provide data at intermediate levels of analysis

        ProcessingModules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """

    __nwbfields__ = ('description',)

    __clsconf__ = {
            'attr': 'data_interfaces',
            'add': 'add',
            'type': (NWBDataInterface, DynamicTable),
            'get': 'get'
    }

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'data_interfaces', 'type': (list, tuple, dict),
             'doc': 'NWBDataInterfacess that belong to this ProcessingModule', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ProcessingModule, self).__init__, kwargs)
        self.description = popargs('description', kwargs)
        self.data_interfaces = popargs('data_interfaces', kwargs)

    @property
    def containers(self):
        return self.data_interfaces

    def __getitem__(self, arg):
        return self.get(arg)

    @docval({'name': 'container', 'type': (NWBDataInterface, DynamicTable),
             'doc': 'the NWBDataInterface to add to this Module'})
    def add_container(self, **kwargs):
        '''
        Add an NWBContainer to this ProcessingModule
        '''
        container = getargs('container', kwargs)
        warn(PendingDeprecationWarning('add_container will be replaced by add'))
        self.add(container)

    @docval({'name': 'container_name', 'type': str, 'doc': 'the name of the NWBContainer to retrieve'})
    def get_container(self, **kwargs):
        '''
        Retrieve an NWBContainer from this ProcessingModule
        '''
        container_name = getargs('container_name', kwargs)
        warn(PendingDeprecationWarning('get_container will be replaced by get'))
        return self.get(container_name)

    @docval({'name': 'NWBDataInterface', 'type': (NWBDataInterface, DynamicTable),
             'doc': 'the NWBDataInterface to add to this Module'})
    def add_data_interface(self, **kwargs):
        NWBDataInterface = getargs('NWBDataInterface', kwargs)
        warn(PendingDeprecationWarning('add_data_interface will be replaced by add'))
        self.add(NWBDataInterface)

    @docval({'name': 'data_interface_name', 'type': str, 'doc': 'the name of the NWBContainer to retrieve'})
    def get_data_interface(self, **kwargs):
        data_interface_name = getargs('data_interface_name', kwargs)
        warn(PendingDeprecationWarning('get_data_interface will be replaced by get'))
        return self.get(data_interface_name)


@register_class('TimeSeries', CORE_NAMESPACE)
class TimeSeries(NWBDataInterface):
    """A generic base class for time series data"""
    __nwbfields__ = ("comments",
                     "description",
                     "data",
                     "resolution",
                     "conversion",
                     "unit",
                     "timestamps",
                     "timestamps_unit",
                     "interval",
                     "starting_time",
                     "rate",
                     "starting_time_unit",
                     "control",
                     "control_description",
                     "continuity")

    __time_unit = "seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},  # required
            {'name': 'data', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': ('The data values. The first dimension must be time. '
                     'Can also store binary data, e.g., image frames'),
             'default': None},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'resolution', 'type': (str, 'float'),
             'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': -1.0},
            {'name': 'conversion', 'type': (str, 'float'),
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': 1.0},

            {'name': 'timestamps', 'type': ('array_data', 'data', 'TimeSeries'), 'shape': (None,),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': 'float', 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': 'float', 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset',
             'default': 'no comments'},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset',
             'default': 'no description'},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data',
             'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value',
             'default': None},
            {'name': 'continuity', 'type': str, 'default': None, 'enum': ["continuous", "instantaneous", "step"],
             'doc': 'Optionally describe the continuity of the data. Can be "continuous", "instantaneous", or'
                    '"step". For example, a voltage trace would be "continuous", because samples are recorded from a '
                    'continuous process. An array of lick times would be "instantaneous", because the data represents '
                    'distinct moments in time. Times of image presentations would be  "step" because the picture '
                    'remains the same until the next time-point. This field is optional, but is useful in providing '
                    'information about the underlying data. It may inform the way this data is interpreted, the way it '
                    'is visualized, and what analysis methods are applicable.'})
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """

        call_docval_func(super(TimeSeries, self).__init__, kwargs)
        keys = ("resolution",
                "comments",
                "description",
                "conversion",
                "unit",
                "control",
                "control_description",
                "continuity")
        for key in keys:
            val = kwargs.get(key)
            if val is not None:
                setattr(self, key, val)

        data = getargs('data', kwargs)
        self.fields['data'] = data

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None:
            if rate is not None:
                raise ValueError('Specifying rate and timestamps is not supported.')
            if starting_time is not None:
                raise ValueError('Specifying starting_time and timestamps is not supported.')
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = self.__time_unit
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.__add_link('timestamp_link', self)
        elif rate is not None:
            self.rate = rate
            if starting_time is not None:
                self.starting_time = starting_time
            else:
                self.starting_time = 0.0
            self.starting_time_unit = self.__time_unit
        else:
            raise TypeError("either 'timestamps' or 'rate' must be specified")

    @property
    def num_samples(self):
        ''' Tries to return the number of data samples. If this cannot be assessed, returns None.
        '''

        def unreadable_warning(attr):
            return (
                'The {} attribute on this TimeSeries (named: {}) has a __len__, '
                'but it cannot be read'.format(attr, self.name)
            )

        def no_len_warning(attr):
            return 'The {} attribute on this TimeSeries (named: {}) has no __len__'.format(attr, self.name)

        if hasattr(self.data, '__len__'):
            try:
                return len(self.data)  # for an ndarray this will return the first element of shape
            except TypeError:
                warn(unreadable_warning('data'), UserWarning)
        else:
            warn(no_len_warning('data'), UserWarning)

        if hasattr(self, 'timestamps'):
            if hasattr(self.timestamps, '__len__'):
                try:
                    return len(self.timestamps)
                except TypeError:
                    warn(unreadable_warning('timestamps'), UserWarning)
            elif not (hasattr(self, 'rate') and hasattr(self, 'starting_time')):
                warn(no_len_warning('timestamps'), UserWarning)

    @property
    def data(self):
        if isinstance(self.fields['data'], TimeSeries):
            return self.fields['data'].data
        else:
            return self.fields['data']

    @property
    def data_link(self):
        return self.__get_links('data_link')

    @property
    def timestamps(self):
        if 'timestamps' not in self.fields:
            return None
        if isinstance(self.fields['timestamps'], TimeSeries):
            return self.fields['timestamps'].timestamps
        else:
            return self.fields['timestamps']

    @property
    def timestamp_link(self):
        return self.__get_links('timestamp_link')

    def __get_links(self, links):
        ret = self.fields.get(links, list())
        if ret is not None:
            ret = set(ret)
        return ret

    def __add_link(self, links_key, link):
        self.fields.setdefault(links_key, list()).append(link)

    @property
    def time_unit(self):
        return self.__time_unit


@register_class('Image', CORE_NAMESPACE)
class Image(NWBData):
    """
    Abstract image class. It is recommended to instead use pynwb.image.GrayscaleImage or pynwb.image.RGPImage where
    appropriate.
    """
    __nwbfields__ = ('data', 'resolution', 'description')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this image'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image. Dimensions: x, y [, r,g,b[,a]]',
             'shape': ((None, None), (None, None, 3), (None, None, 4))},
            {'name': 'resolution', 'type': 'float', 'doc': 'pixels / cm', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'description of image', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(Image, self).__init__, kwargs)
        self.resolution = kwargs['resolution']
        self.description = kwargs['description']


@register_class('Images', CORE_NAMESPACE)
class Images(MultiContainerInterface):

    __nwbfields__ = ('description',)

    __clsconf__ = {
        'attr': 'images',
        'add': 'add_image',
        'type': Image,
        'get': 'get_image',
        'create': 'create_image'
    }

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this set of images'},
            {'name': 'images', 'type': 'array_data', 'doc': 'image objects', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'description of images', 'default': 'no description'})
    def __init__(self, **kwargs):
        name, description, images = popargs('name', 'description', 'images', kwargs)
        super(Images, self).__init__(name, **kwargs)
        self.description = description
        self.images = images


@register_class('TimeSeriesReferenceVectorData', CORE_NAMESPACE)
class TimeSeriesReferenceVectorData(VectorData):
    """
    Column storing references to a TimeSeries (rows). For each TimeSeries this VectorData
    column stores the start_index and count to indicate the range in time to be selected
    as well as an object reference to the TimeSeries.

    In practice we sometimes need to be able to represent missing values, e.g., in the
    IntracellularRecordingsTable we have TimeSeriesReferenceVectorData for stimulus and
    response but a user can specify either only one of them or both. Since there is no
    "None" value for a complex type like (idx_start, count, TimeSeries), we internally
    define None as (-1, -1, TimeSeries), i.e., if the idx_start and/or count is negative
    then this indicates an invalid link (in practice both idx_start and count should always
    either both be positive or both be negative). When selecting data via the
    TimeSeriesReferenceVectorData.get and TimeSeriesReferenceVectorData.__getitem__
    functions, (-1, -1, TimeSeries) are masked in the resulting np.ma.masked_array or
    represented as a np.ma.core.MaskedConstant()
    """
    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData', 'default': 'timeseries'},
            {'name': 'description', 'type': str, 'doc': 'a description for this column',
             'default': "Column storing references to a TimeSeries (rows). For each TimeSeries this "
                        "VectorData column stores the start_index and count to indicate the range in time "
                        "to be selected as well as an object reference to the TimeSeries."},
            *get_docval(VectorData.__init__, 'data'))
    def __init__(self, **kwargs):
        call_docval_func(super().__init__, kwargs)

    def get(self, key, **kwargs):
        """
        Retrieve elements from this TimeSeriesReferenceVectorData

        :param key: Selection of the elements
        :param kwargs: Ignored
        """
        vals = super().get(key)
        # we only selected one row.
        if isinstance(key, (int, np.integer)):
            # NOTE: If we never wrote the data to disk, then vals will be a single tuple.
            #       If the data is loaded from an h5py.Dataset then vals will be a single
            #       np.void object. I.e., and alternative check would be
            #       if isinstance(vals, tuple) or isinstance(vals, np.void):
            #          ...
            if vals[0] < 0 or vals[1] < 0:
                return np.ma.core.MaskedArray(data=vals, mask=[True, True, True])
            else:
                return vals
        else:  # key selected multiple rows
            # When loading from HDF5 we get an np.ndarray otherwise we get list-of-list. This
            # makes things the values consistent
            if isinstance(vals, np.ndarray):
                vals = [[v[0], v[1], v[2]] for v in vals]
            vals = np.asarray(vals)
            mask = np.asarray([(v[0] < 0 or v[1] < 0) for v in vals])
            # For some reason, when we only select 0 or 1 element it is sufficient to mask that element
            # but when selecting more than 1 element we need to mask all 3 components of each element
            if len(vals) > 1:
                mask = np.asarray([v for v in mask for i in range(3)])
            # If we are masking any elements than create a masked array
            if np.any(mask):
                # Depending on whether we select 1 or multiple values we need to for some reason
                # either define mask values for ea
                return np.ma.masked_array(vals, mask)
            else:  # otherwise just use a regular (unmasked) ndarray
                return np.asarray(vals)

    def extend(self, ar):
        """
        The extend_data method adds all the elements of the iterable arg to the
        end of the data of this Data container.

        :param arg: The iterable to add to the end of this VectorData
        """
        self.data = extend_data(self.data, ar)
