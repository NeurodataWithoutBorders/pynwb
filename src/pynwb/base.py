from warnings import warn
from bisect import bisect
import numpy as np

from collections import Iterable

from .form.utils import docval, getargs, popargs, fmt_docval_args, call_docval_func
from .form.data_utils import AbstractDataChunkIterator, DataIO

from . import register_class, CORE_NAMESPACE, NWBFile
from .core import NWBDataInterface, MultiContainerInterface, NWBData

_default_conversion = 1.0
_default_resolution = 0.0


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
            'add': 'add_data_interface',
            'type': NWBDataInterface,
            'get': 'get_data_interface'
    }

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'data_interfaces', 'type': (list, tuple, dict),
             'doc': 'NWBDataInterfacess that belong to this ProcessingModule', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ProcessingModule, self).__init__, kwargs)
        self.description = popargs('description', kwargs)
        self.data_interfaces = popargs('data_interfaces', kwargs)

    @property
    def containers(self):
        return self.data_interfaces

    def __getitem__(self, arg):
        return self.get_data_interface(arg)

    @docval({'name': 'container', 'type': NWBDataInterface, 'doc': 'the NWBDataInterface to add to this Module'})
    def add_container(self, **kwargs):
        '''
        Add an NWBContainer to this ProcessingModule
        '''
        container = getargs('container', kwargs)
        warn(PendingDeprecationWarning('add_container will be replaced by add_data_interface'))
        self.add_data_interface(container)

    @docval({'name': 'container_name', 'type': str, 'doc': 'the name of the NWBContainer to retrieve'})
    def get_container(self, **kwargs):
        '''
        Retrieve an NWBContainer from this ProcessingModule
        '''
        container_name = getargs('container_name', kwargs)
        warn(PendingDeprecationWarning('get_container will be replaced by get_data_interface'))
        return self.get_data_interface(container_name)


@register_class('TimeSeries', CORE_NAMESPACE)
class TimeSeries(NWBDataInterface):
    """A generic base class for time series data"""
    __nwbfields__ = ("comments",
                     "description",
                     "data",
                     "resolution",
                     "conversion",
                     "unit",
                     "num_samples",
                     "timestamps",
                     "timestamps_unit",
                     "interval",
                     "starting_time",
                     "rate",
                     "starting_time_unit",
                     "control",
                     "control_description")

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'resolution', 'type': (str, float),
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': (str, float),
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},

            {'name': 'timestamps', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """
        pargs, pkwargs = fmt_docval_args(super(TimeSeries, self).__init__, kwargs)
        super(TimeSeries, self).__init__(*pargs, **pkwargs)
        keys = ("resolution",
                "comments",
                "description",
                "conversion",
                "unit",
                "control",
                "control_description")
        for key in keys:
            val = kwargs.get(key)
            if val is not None:
                setattr(self, key, val)

        data = getargs('data', kwargs)
        self.fields['data'] = data
        if isinstance(data, TimeSeries):
            data.__add_link('data_link', self)
            self.fields['num_samples'] = data.num_samples
        elif isinstance(data, AbstractDataChunkIterator):
            self.fields['num_samples'] = -1
        elif isinstance(data, DataIO):
            this_data = data.data
            if isinstance(this_data, AbstractDataChunkIterator):
                self.fields['num_samples'] = -1
            else:
                self.fields['num_samples'] = len(this_data)
        elif data is None:
            self.fields['num_samples'] = 0
        else:
            self.fields['num_samples'] = len(data)

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None:
            if rate is not None:
                raise ValueError('Specifying rate and timestamps is not supported.')
            if starting_time is not None:
                raise ValueError('Specifying starting_time and timestamps is not supported.')
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = 'Seconds'
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.__add_link('timestamp_link', self)
        elif rate is not None:
            self.rate = rate
            if starting_time is not None:
                self.starting_time = starting_time
                self.starting_time_unit = 'Seconds'
            else:
                self.starting_time = 0.0
        else:
            raise TypeError("either 'timestamps' or 'rate' must be specified")

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

    def align_by_trials(self, **kwargs):
        """

        Args:
            start_label: str
                default: 'start_time'
            stop_label: str
                default: 'stop_time'
            before: float
                time after start_label in secs (positive goes back in time)
            after:
                time after stop_label in secs (positive goes forward in time)

        Returns:
            np.array(shape=(n_trials, n_time, ...))

        """
        trials = self.get_ancestor(NWBFile).intervals.trials
        return self.align_by_intervals(trials, **kwargs)

    def align_by_intervals(self, intervals, start_label='start_time',
                           stop_label='stop_time', before=0., after=0.):
        """

        Args:
            intervals: pynwb.Intervals
            start_label: str
                default: 'start_time'
            stop_label: str
                default: 'stop_time'
            before: float
                time after start_label in secs (positive goes back in time)
            after:
                time after stop_label in secs (positive goes forward in time)

        Returns:
            np.array(shape=(n_trials, n_time, ...))

        """
        if stop_label is None:
            stop_label = 'start_time'

        starts = intervals[start_label][:] - before
        stops = intervals[stop_label][:] + after
        return self.align_by_times(starts, stops)

    def align_by_times(self, starts, stops):
        """

        Args:
            starts: array-like
            stops: array-like

        Returns:
            np.array(shape=(n_trials, n_time, ...))

        """
        out = []
        for istart, istop in zip(starts, stops):
            if self.timestamps is not None:
                ind_start = bisect(self.timestamps, istart)
                ind_stop = bisect(self.timestamps, istop)
                out.append(self.data[ind_start:ind_stop, ...])
            else:
                ind_start = (istart - self.starting_time) / self.rate
                ind_stop = ind_start + (istop - istart) / self.rate
                out.append(self.data[ind_start:ind_stop, ...])
        return np.array(out)


@register_class('Image', CORE_NAMESPACE)
class Image(NWBData):
    __nwbfields__ = ('data', 'resolution', 'description')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image',
             'shape': ((None, None), (None, None, 3), (None, None, 4))},
            {'name': 'resolution', 'type': float, 'doc': 'pixels / cm', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'description of image', 'default': None})
    def __init__(self, **kwargs):
        super(Image, self).__init__(name=kwargs['name'], data=kwargs['data'])
        self.resolution = kwargs['resolution']
        self.description = kwargs['description']


@register_class('Images', CORE_NAMESPACE)
class Images(MultiContainerInterface):

    __clsconf__ = {
        'attr': 'images',
        'add': 'add_image',
        'type': Image,
        'get': 'get_image',
        'create': 'create_image'
    }

    __help = "Contains images"
