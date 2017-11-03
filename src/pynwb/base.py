from collections import Iterable

from .form.utils import docval, getargs, popargs, fmt_docval_args
from .form.data_utils import DataChunkIterator

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer

_default_conversion = 1.0
_default_resolution = 0.0


@register_class('ProcessingModule', CORE_NAMESPACE)
class ProcessingModule(NWBContainer):
    """ Processing module. This is a container for one or more containers
        that provide data at intermediate levels of analysis

        ProcessingModules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """

    __nwbfields__ = ('description',
                     'containers')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'containers', 'type': (list, dict),
             'doc': 'NWBContainers that belong to this ProcessingModule', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        description, containers = popargs('description', 'containers', kwargs)
        super(ProcessingModule, self).__init__(**kwargs)
        self.description = description
        self.__containers = self.__to_dict(containers)

    def __to_dict(self, arg):
        if arg is None:
            return dict()
        else:
            return_dict = {}
            for i in arg:
                assert i.name is not None  # If a container doesn't have a name, it gets lost!
                assert i.name not in return_dict
                return_dict[i.name] = i
            return return_dict

    @property
    def containers(self):
        return tuple(self.__containers.values())

    @docval({'name': 'container', 'type': NWBContainer, 'doc': 'the NWBContainer to add to this Module'})
    def add_container(self, **kwargs):
        '''
        Add an NWBContainer to this ProcessingModule
        '''
        container = getargs('container', kwargs)
        self.__containers[container.name] = container
        container.parent = self

    @docval({'name': 'container_name', 'type': str, 'doc': 'the name of the NWBContainer to retrieve'})
    def get_container(self, **kwargs):
        '''
        Retrieve an NWBContainer from this ProcessingModule
        '''
        container_name = getargs('container_name', kwargs)
        return self.__containers.get(container_name)


@register_class('TimeSeries', CORE_NAMESPACE)
class TimeSeries(NWBContainer):
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
                     "rate_unit",
                     "control",
                     "control_description",
                     "ancestry",
                     "neurodata_type",
                     "help")

    __ancestry = 'TimeSeries'
    __neurodata_type = 'TimeSeries'
    __help = 'General purpose TimeSeries'

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': (Iterable, 'TimeSeries', DataChunkIterator),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'resolution', 'type': (str, float),
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': (str, float),
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},

            # time related data is optional, but one is required -- this will have to be enforced in the constructor
            {'name': 'timestamps', 'type': (Iterable, 'TimeSeries', DataChunkIterator),
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
            data.fields['data_link'].append(self)
            self.fields['num_samples'] = data.num_samples
        elif isinstance(data, DataChunkIterator):
            self.fields['num_samples'] = -1
        else:
            self.fields['num_samples'] = len(data)

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None:
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = 'Seconds'
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.fields['timestamp_link'].append(self)
        elif starting_time is not None and rate is not None:
            self.starting_time = starting_time
            self.rate = rate
            self.rate_unit = 'Seconds'
        else:
            raise TypeError("either 'timestamps' or 'starting_time' and 'rate' must be specified")

        # self.fields['data_link'] = set()
        # self.fields['timestamp_link'] = set()

    @property
    def help(self):
        return self.__help

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
