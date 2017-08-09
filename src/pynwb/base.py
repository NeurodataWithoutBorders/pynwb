import numpy as np
from collections import Iterable

from form.utils import docval, getargs, popargs, DataChunkIterator, fmt_docval_args

from . import register_class, CORE_NAMESPACE
from .core import  NWBContainer

_default_conversion = 1.0
_default_resolution = 0.0

#@register_class('Interface', CORE_NAMESPACE)
#class Interface(NWBContainer):
#    """ Interfaces represent particular processing tasks and they publish
#        (ie, make available) specific types of data. Each is required
#        to supply a minimum of specifically named data, but all can store
#        data beyond this minimum
#
#        Interfaces should be created through Module.create_interface().
#        They should not be created directly
#    """
#    __nwbfields__ = ("help",
#                     "neurodata_type",
#                     "source")
#
#    __neurodata_type = "Interface"
#
#    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Interface'},
#            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
#    def __init__(self, **kwargs):
#        if self.__class__ == Interface:
#            raise NotImplementedError("Interface cannot by instantiated directly")
#        source = getargs('source', kwargs)
#        super(Interface, self).__init__(**kwargs)
#        self.source = source
#
#    @property
#    def name(self):
#        #name_attr_name = '_%s__name' % str(self.__class__.__name__).lstrip('_')
#        #if hasattr(self, name_attr_name):
#        #    return getattr(self, name_attr_name)
#        #else:
#        #    return self.__class__.__name__
#        return self.__class__.__name__
#        return None
#
#    @property
#    def help(self):
#        help_attr_name = '_%s__help' % str(self.__class__.__name__).lstrip('_')
#        if hasattr(self, help_attr_name):
#            return getattr(self, help_attr_name)
#        return None

@register_class('ProcessingModule', CORE_NAMESPACE)
class ProcessingModule(NWBContainer):
    """ Processing module. This is a container for one or more containers
        that provide data at intermediate levels of analysis

        Modules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """

    __nwbfields__ = ('description',
                     'containers')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'containers', 'type': list, 'doc': 'NWBContainers that belong to this Modules', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, description, containers = popargs('name', 'description', 'containers', kwargs)
        super(Module, self).__init__(**kwargs)
        self.description = description
        self.__containers = list() if containers is None else containers

    @property
    def containers(self):
        return tuple(self.__containers)

    @docval({'name': 'container', 'type': NWBContainer, 'doc': 'the NWBContainer to add to this Module'})
    def add_container(self, **kwargs):
        container = getargs('container', kwargs)
        self.__containers.append(container)
        container.parent = self

@register_class('TimeSeries', CORE_NAMESPACE)
class TimeSeries(NWBContainer):
    """ Standard TimeSeries constructor

        All time series are created by calls to  NWB.create_timeseries().
        They should not not be instantiated directly
    """
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
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (Iterable, 'TimeSeries', DataChunkIterator), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'resolution', 'type': (str, float), 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': (str, float), 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},

            ## time related data is optional, but one is required -- this will have to be enforced in the constructor
            {'name': 'timestamps', 'type': (Iterable, 'TimeSeries', DataChunkIterator), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """
        pargs, pkwargs = fmt_docval_args(super().__init__, kwargs)
        super().__init__(*pargs, **pkwargs)
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

        #self.fields['data_link'] = set()
        #self.fields['timestamp_link'] = set()

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

    @docval({'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset'})
    def set_description(self, **kwargs):
        """ Convenience function to set the description field of the
            *TimeSeries*
        """
        self.fields['description'] = kwargs['description']

    @docval({'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset'})
    def set_comments(self, **kwargs):
        """ Convenience function to set the comments field of the
            *TimeSeries*
        """
        self.fields['comments'] = kwargs['comments']
