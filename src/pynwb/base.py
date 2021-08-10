from warnings import warn
from collections.abc import Iterable
import numpy as np
from typing import NamedTuple

from hdmf.utils import docval, getargs, popargs, call_docval_func, get_docval
from hdmf.common import DynamicTable, VectorData

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

    # values used when a TimeSeries is read and missing required fields
    DEFAULT_DATA = np.ndarray(shape=(0, ), dtype=np.uint8)
    DEFAULT_UNIT = 'unknown'

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},  # required
            {'name': 'data', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': ('The data values. The first dimension must be time. '
                     'Can also store binary data, e.g., image frames')},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
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


class TimeSeriesReference(NamedTuple):
    """
    Class used to represent data values of a :py:class:`~pynwb.base.TimeSeriesReferenceVectorData`
    This is a ``typing.NamedTuple`` type with predefined tuple components
    :py:meth:`~pynwb.base.TimeSeriesReference.idx_start`, :py:meth:`~pynwb.base.TimeSeriesReference.count`, and
    :py:meth:`~pynwb.base.TimeSeriesReference.timeseries`.

    :cvar idx_start:
    :cvar count:
    :cvar timeseries:
    """
    idx_start: int
    """Start index in time for the timeseries"""

    count: int
    """Number of timesteps to be selected starting from :py:meth:`~pynwb.base.TimeSeriesReference.idx_start`"""

    timeseries: TimeSeries
    """The :py:class:`~pynwb.base.TimeSeries` object the TimeSeriesReference applies to"""

    def check_types(self):
        """
        Helper function to check correct types for :py:meth:`~pynwb.base.TimeSeriesReference.idx_start`,
        :py:meth:`~pynwb.base.TimeSeriesReference.count`, and :py:meth:`~pynwb.base.TimeSeriesReference.timeseries`.

        This function is usually used in the try/except block to check for `TypeError` raised by the function.

        See also :py:meth:`~pynwb.base.TimeSeriesReference.isvalid` to check both validity of types and the
        reference itself.

        :returns: True if successful. If unsuccessful `TypeError` is raised.

        :raises TypeError: If one of the fields does not match the expected type
        """
        if not isinstance(self.idx_start, (int, np.integer)):
            raise TypeError("idx_start must be an integer not %s" % str(type(self.idx_start)))
        if not isinstance(self.count, (int, np.integer)):
            raise TypeError("count must be an integer %s" % str(type(self.count)))
        if not isinstance(self.timeseries, TimeSeries):
            raise TypeError("timeseries must be of type TimeSeries. %s" % str(type(self.timeseries)))
        return True

    def isvalid(self):
        """
        Check whether the reference is valid. Setting :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and
        :py:meth:`~pynwb.base.TimeSeriesReference.count` to -1 is used to indicate invalid references. This is
        useful to allow for missing data in :py:class:`~pynwb.base.TimeSeriesReferenceVectorData`

        :returns: True if the selection is valid. Returns False if both
            :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and :py:meth:`~pynwb.base.TimeSeriesReference.count`
            are negative. Raises `IndexError` in case the indices are bad.

        :raises IndexError: If the combination of :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and
            :py:meth:`~pynwb.base.TimeSeriesReference.count` are not valid for the given timeseries.

        :raises TypeError: If one of the fields does not match the expected type
        """
        # Check types first
        self.check_types()
        # Check for none-type selection
        if self.idx_start < 0 and self.count < 0:
            return False
        num_samples = self.timeseries.num_samples
        if num_samples is not None:
            if self.idx_start >= num_samples or self.idx_start < 0:
                raise IndexError("'idx_start' %i out of range for timeseries '%s'" %
                                 (self.idx_start, self.timeseries.name))
            if self.count < 0:
                raise IndexError("'count' %i invalid. 'count' must be positive" % self.count)
            if (self.idx_start + self.count) > num_samples:
                raise IndexError("'idx_start + count' out of range for timeseries '%s'" % self.timeseries.name)
        return True

    @property
    def timestamps(self):
        """
        Get the floating point timestamp offsets in seconds from the timeseries that correspond to the array.
        These are either loaded directly from the :py:meth:`~pynwb.base.TimeSeriesReference.timeseries`
        timestamps or calculated from the starting time and sampling rate.


        :raises IndexError: If the combination of :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and
            :py:meth:`~pynwb.base.TimeSeriesReference.count` are not valid for the given timeseries.

        :raises TypeError: If one of the fields does not match the expected type

        :returns: Array with the timestamps.
        """
        # isvalid will be False only if both idx_start and count are negative. Otherwise well get errors or be True.
        if not self.isvalid():
            return None
        # load the data from the timestamps
        elif self.timeseries.timestamps is not None:
            return self.timeseries.timestamps[self.idx_start: (self.idx_start + self.count)]
        # construct the timestamps from the starting_time and rate
        else:
            start_time = self.timeseries.rate * self.idx_start + self.timeseries.starting_time
            return np.arange(0, self.count) * self.timeseries.rate + start_time

    @property
    def data(self):
        """
        Get the selected data values. This is a convenience function to slice data from the
        :py:meth:`~pynwb.base.TimeSeriesReference.timeseries` based on the given
        :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and
        :py:meth:`~pynwb.base.TimeSeriesReference.count`

        :raises IndexError: If the combination of :py:meth:`~pynwb.base.TimeSeriesReference.idx_start` and
            :py:meth:`~pynwb.base.TimeSeriesReference.count` are not valid for the given timeseries.

        :raises TypeError: If one of the fields does not match the expected type

        :returns: Result of ``self.timeseries.data[self.idx_start: (self.idx_start + self.count)]``. Returns
            None in case the reference is invalid (i.e., if both :py:meth:`~pynwb.base.TimeSeriesReference.idx_start`
            and :py:meth:`~pynwb.base.TimeSeriesReference.count` are negative.
        """
        # isvalid will be False only if both idx_start and count are negative. Otherwise well get errors or be True.
        if not self.isvalid():
            return None
        # load the data from the timeseries
        return self.timeseries.data[self.idx_start: (self.idx_start + self.count)]


@register_class('TimeSeriesReferenceVectorData', CORE_NAMESPACE)
class TimeSeriesReferenceVectorData(VectorData):
    """
    Column storing references to a TimeSeries (rows). For each TimeSeries this VectorData
    column stores the start_index and count to indicate the range in time to be selected
    as well as an object reference to the TimeSeries.

    **Representing missing values** In practice we sometimes need to be able to represent missing values,
    e.g., in the :py:class:`~pynwb.icephys.IntracellularRecordingsTable` we have
    :py:class:`~pynwb.base.TimeSeriesReferenceVectorData` to link to stimulus and
    response recordings, but a user can specify either only one of them or both. Since there is no
    ``None`` value for a complex types like ``(idx_start, count, TimeSeries)``, NWB defines
    ``None`` as ``(-1, -1, TimeSeries)`` for storage, i.e., if the ``idx_start`` (and ``count``) is negative
    then this indicates an invalid link (in practice both ``idx_start`` and ``count`` must always
    either both be positive or both be negative). When selecting data via the
    :py:meth:`~pynwb.base.TimeSeriesReferenceVectorData.get` or
    :py:meth:`~pynwb.base. TimeSeriesReferenceVectorData.__getitem__`
    functions, ``(-1, -1, TimeSeries)`` values are replaced by the corresponding
    :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE` tuple
    to avoid exposing NWB storage internals to the user and simplifying the use of and checking
    for missing values. **NOTE:** We can still inspect the raw data values by looking at ``self.data``
    directly instead.

    :cvar TIME_SERIES_REFERENCE_TUPLE:
    :cvar TIME_SERIES_REFERENCE_NONE_TYPE:
    """

    TIME_SERIES_REFERENCE_TUPLE = TimeSeriesReference
    """Return type when calling :py:meth:`~pynwb.base.TimeSeriesReferenceVectorData.get` or
    :py:meth:`~pynwb.base. TimeSeriesReferenceVectorData.__getitem__`."""

    TIME_SERIES_REFERENCE_NONE_TYPE = TIME_SERIES_REFERENCE_TUPLE(None, None, None)
    """Tuple used to represent None values when calling :py:meth:`~pynwb.base.TimeSeriesReferenceVectorData.get` or
    :py:meth:`~pynwb.base. TimeSeriesReferenceVectorData.__getitem__`. See also
    :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE`"""

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData', 'default': 'timeseries'},
            {'name': 'description', 'type': str, 'doc': 'a description for this column',
             'default': "Column storing references to a TimeSeries (rows). For each TimeSeries this "
                        "VectorData column stores the start_index and count to indicate the range in time "
                        "to be selected as well as an object reference to the TimeSeries."},
            *get_docval(VectorData.__init__, 'data'))
    def __init__(self, **kwargs):
        call_docval_func(super().__init__, kwargs)

    @docval({'name': 'val', 'type': TIME_SERIES_REFERENCE_TUPLE, 'doc': 'the value to add to this column'})
    def add_row(self, **kwargs):
        """Append a data value to this column."""
        val = getargs('val', kwargs)
        val.check_types()
        super().append(val)

    @docval({'name': 'arg', 'type': TIME_SERIES_REFERENCE_TUPLE, 'doc': 'the value to append to this column'})
    def append(self, **kwargs):
        """Append a data value to this column."""
        arg = getargs('arg', kwargs)
        arg.check_types()
        super().append(arg)

    def get(self, key, **kwargs):
        """
        Retrieve elements from this object.

        The function uses :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE`
        to describe individual records in the dataset. This allows the code to avoid exposing internal
        details of the schema to the user and simplifies handling of missing values by explictly
        representing missing values via
        :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE`
        rather than the internal representation used for storage of ``(-1, -1, TimeSeries)``.

        :param key: Selection of the elements
        :param kwargs: Ignored

        :returns: :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE` if a single
                  element is being selected. Otherwise return a list of
                  :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE` objects.
                  Missing values are represented by
                  :py:class:`~pynwb.base.TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE`
                  in which all values (i.e., idx_start, count, timeseries) are set to None.
        """
        vals = super().get(key)
        # we only selected one row.
        if isinstance(key, (int, np.integer)):
            # NOTE: If we never wrote the data to disk, then vals will be a single tuple.
            #       If the data is loaded from an h5py.Dataset then vals will be a single
            #       np.void object. I.e., an alternative check would be
            #       if isinstance(vals, tuple) or isinstance(vals, np.void):
            #          ...
            if vals[0] < 0 or vals[1] < 0:
                return self.TIME_SERIES_REFERENCE_NONE_TYPE
            else:
                return self.TIME_SERIES_REFERENCE_TUPLE(*vals)
        else:  # key selected multiple rows
            # When loading from HDF5 we get an np.ndarray otherwise we get list-of-list. This
            # makes the values consistent and tranforms the data to use our namedtuple type
            re = [self.TIME_SERIES_REFERENCE_NONE_TYPE
                  if (v[0] < 0 or v[1] < 0) else self.TIME_SERIES_REFERENCE_TUPLE(*v)
                  for v in vals]
            return re
