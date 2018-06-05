from warnings import warn

from collections import Iterable

from .form.utils import docval, getargs, popargs, fmt_docval_args
from .form.data_utils import AbstractDataChunkIterator, DataIO

from . import register_class, CORE_NAMESPACE
from .core import NWBDataInterface, MultiContainerInterface

from numpy import ndarray
from copy import copy
from .form.array import LinSpace, SortedArray

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
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'data_interfaces', 'type': (list, tuple, dict),
             'doc': 'NWBDataInterfacess that belong to this ProcessingModule', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        description = popargs('description', kwargs)
        super(ProcessingModule, self).__init__(**kwargs)
        self.description = description
        self.data_interfaces = getargs('data_interfaces', kwargs)

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
                     "rate_unit",
                     "control",
                     "control_description",
                     "help")

    __help = 'General purpose TimeSeries'

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
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
            data.fields['data_link'].append(self)
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

    @docval({'name': 'as_sortedarray', 'type': bool, 'doc': 'If True, return form.array.SortedArray for timestamps',
             'default': True})
    def get_timestamps(self, **kwargs):
        """
        Get timestamps array

        :return: SortedArray of as_sortedarray is True else return self.timestamps directly
        """
        as_sortedarray = getargs('as_sortedarray', kwargs)
        if as_sortedarray:
            if 'timestamps' not in self.fields:
                return LinSpace(start=self.starting_time,
                                stop=self.starting_time + self.fields['num_samples'] * self.rate,
                                step=self.rate)
            if isinstance(self.fields['timestamps'], TimeSeries):
                return self.fields['timestamps'].get_timestamps(as_sortedarray=as_sortedarray)
            else:
                if isinstance(self.fields['timestamps'], SortedArray):
                    return self.fields['timestamps']
                else:
                    return SortedArray(self.fields['timestamps'], dtype='float')
        else:
            return self.timestamps

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

    @docval({'name': 'time', 'type': float, 'doc': 'The time value to mak to an index in the timeseries'},
            {'name': 'match', 'type': str, 'doc': "Find best matching time 'before' or 'after'.", 'default': 'before'},
            returns="This function returns: 1) the integer index and 2) the floating point time value")
    def time_to_index(self, **kwargs):
        """
        Convert a time value to an index for selection in the timeseries.

        The function will always try to return the index of the exact matching timepoint if available.
        If no exact match for the time is found then the function will return:

        * The closest index before the indicated time if match is set to 'before'
        * The closest index after the indicated time if match is set to 'after'
        * None in case the given time is out of range of the time series

        """
        time, match = getargs('time', 'match', kwargs)
        valid_match_vals = ['before', 'after']
        if match not in valid_match_vals:
            raise ValueError("match=%s invalid. Valid values are one of: %s" % (match, str(valid_match_vals)))
        # Find the closest timestamp in our series
        side = 'left' if match != 'after' else 'right'
        try:
            st = self.get_timestamps(as_sortedarray=True)
            result_index = st.find_point(time, side)
            result_time = st[result_index]
        except ValueError:
            result_index = None
            result_time = None
        return result_index, result_time

    @docval({'name': 'name', 'type': str, 'doc': 'Name of the new subset TimeSeries'},
            {'name': 'time_range', 'type': tuple, 'doc': 'Tuple with start and stop time to select', 'default': None},
            {'name': 'time_match', 'type': tuple,
             'doc': 'Tuple indicting for time_range whether start/stop should be matched "before" or "after".' +
                    'Default behavior is ("after", "before"), i.e., start=after and stop=before',
             'default': None},
            {'name': 'index_select', 'type': tuple, 'doc': 'Selections to be applied to self.data.', 'default': None},
            returns='New TimeSeries with data and timestamps adjustd by the applied selection')
    def subset_series(self, **kwargs):
        new_name, time_range, time_match, index_select = getargs('name', 'time_range', 'time_match', 'index_select',
                                                                 kwargs)
        # No selection applied
        if time_range is None and index_select is None:
            return self

        # Validate that time_range and index_select are compatible
        if time_range is not None and index_select is not None:
            if index_select[0] is not None and index_select != slice(None):
                raise ValueError("time_range=%s not compatible with selection specified by index_select[0]=%s" %
                                 (str(time_range), str(index_select[0])))
        if time_range is not None:
            if len(time_range) != 2:
                raise ValueError('time_range must have length 2')
            if time_match is not None and len(time_match) != 2:
                raise ValueError('time_match must have length 2')

        # If we only have a time_range select, then create an empty index_select so we can update it
        if index_select is None:
            index_select = [slice(None), ]

        # Convert the time_range selection to an index selection and update index_select and new_starting_time
        if time_range is not None:
            if time_match is None:
                time_match = ['after', 'before']
            start_index, start_time = self.time_to_index(time=time_range[0], match=time_match[0])
            stop_index, stop_time = self.time_to_index(time=time_range[1], match=time_match[1])
            if start_index is None:
                raise ValueError("No valid start time found %s %s" % (str(time_match[0]), str(time_range[0])))
            if stop_index is None:
                raise ValueError("No valid stop time found %s %s" % (str(time_match[1]), str(time_range[1])))
            index_select[0] = slice(start_index,    # start
                                    stop_index+1,   # stop = +1 because we need to include the stop
                                    1               # step = Select all elements in the range
                                    )
            new_starting_time = start_time
        # Apply our selection to the data
        if isinstance(self.data, list):
            new_data = self.data
            for s in index_select:
                new_data = new_data[s]
        else:
            new_data = self.data[index_select]

        # Initialize the new starting and end times
        new_sampling_rate = None
        new_starting_time = None
        new_timestamps = None
        if self.timestamps is not None:
            new_sampling_rate = None
            new_starting_time = None
            new_timestamps = self.timestamps
        else:
            new_timestamps = None
            new_sampling_rate = self.rate
            start_index = 0
            if isinstance(index_select[0], slice):
                start_index = index_select[0].start
            elif isinstance(index_select[0], list) or isinstance(index_select[0], ndarray):
                start_index = index_select[0][0]
            elif isinstance(index_select[0], int):
                start_index = index_select[0]
            else:
                raise NotImplementedError("Could not determine new start time from selection %s" % str(index_select[0]))
            new_starting_time = self.starting_time + self.rate * start_index

        new_fields = dict(data=new_data,
                          timestamps=new_timestamps,
                          sampling_rate=new_sampling_rate,
                          start_time=new_starting_time)
        for k, v in self.fields.items():
            if k not in new_fields:  # ignore fields we have already set explicitly
                new_fields[k] = copy(v)
        return self.__class__(name=new_name, **new_fields)
