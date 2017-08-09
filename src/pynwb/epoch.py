import copy
import numpy as np
from bisect import bisect_left

from form.utils import docval, getargs

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import NWBContainer

#@nwbproperties(*__std_fields, neurodata_type='Epoch')
@register_class('Epoch', CORE_NAMESPACE)
class Epoch(NWBContainer):
    """ Epoch object
        Epochs represent specific experimental intervals and store
        references to desired time series that overlap with the interval.
        The references to those time series indicate the first
        index in the time series that overlaps with the interval, and the
        duration of that overlap.

        Epochs should be created through NWBFile.create_epoch(). They should
        not be instantiated directly
    """
    __nwbfields__ = ('name',
                     'description',
                     'start_time',
                     'stop_time',
                     'tags',
                     'links')


    #_neurodata_type = 'Epoch'

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the epoch, as it will appear in the file'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'start', 'type': float, 'doc': 'the starting time of the epoch'},
            {'name': 'stop', 'type': float, 'doc': 'the ending time of the epoch'},
            {'name': 'description', 'type': str, 'doc': 'a description of this epoch', 'default': None},
            {'name': 'tags', 'type': (tuple, list), 'doc': 'tags for this epoch', 'default': list()},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, start, stop, description, tags, parent = getargs('name', 'start', 'stop', 'description', 'tags', 'parent', kwargs)
        super(Epoch, self).__init__(parent=parent)
        # dict to keep track of which time series are linked to this epoch
        self._timeseries = dict()
        # start and stop time (in seconds)
        self.start_time = start
        self.stop_time = stop
        # name of epoch
        self.name = name
        self.description = description

        self.tags = list({x for x in tags})

    @property
    def links(self):
        return []  # TODO need to implement links

    @property
    def timeseries(self):
        return tuple(self._timeseries.values())

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'})
    def get_timeseries(self, **kwargs):
        name = getargs('name', kwargs)
        ts = self._timeseries.get(name)
        if ts:
            return ts
        else:
            raise KeyError("TimeSeries '%s' not found in Epoch '%s'" % (name, self.name))


    def set_description(self, desc):
        """ Convenience function to set the value of the 'description'
            dataset in the epoch

            Arguments:
                *desc* (text) Description of the epoch

            Returns:
                *nothing*
        """
        self.description = desc

    def add_tag(self, tag):
        """ Append string annotation to epoch. This will be stored in
            the epoch's 'tags' dataset. Additionally, it will be added
            to a master tag list stored as an attribute on the root
            'epoch/' group. Each epoch can have multiple tags. The root
            epoch keeps a list of unique tags

            Arguments:
                *tag* (text) Name of the tag to add to the epoch

            Returns:
                *nothing*
        """
        i = bisect_left(self.tags, tag)
        if i == len(self.tags) or self.tags[i] != tag:
            self.tags.insert(i, tag)


    # limit intervals to time boundary of epoch, but don't perform
    #   additional logic (ie, if user supplies overlapping intervals,
    #   let them do so
    def add_ignore_interval(self, start, stop):
        """ Each epoch has a list of intervals that can be flagged to
            be ignored, for example due electrical noise or poor behavior
            of the subject. Intervals are trimmed to fit within epoch
            boundaries, but no further logic is performed (eg, if overlapping
            intervals are specified, those overlaps will be stored)

            Arguments:
                *start* (float) Start of the interval to ignore

                *stop* (float) End time of the interval

            Returns:
                *nothing*
        """
        if start > self.stop_time or stop < self.start_time:
            return  # non-overlapping
        if start < self.start_time:
            start = self.start_time
        if stop > self.stop_time:
            stop = self.stop_time
        self.spec["ignore_intervals"]["_value"].append([start, stop])

    def add_timeseries(self, timeseries, in_epoch_name=None):
        """ Associates time series with epoch. This will create a link
            to the specified time series within the epoch and will
            calculate its overlaps.

            Arguments:
                *in_epoch_name* (text) Name that time series will use
                in the epoch (this can be different than the actual
                time series name)

                *timeseries* (text or TimeSeries object)
                Full hdf5 path to time series that's being added,
                or the TimeSeries object itself

            Returns:
                *nothing*
        """
        name = in_epoch_name if in_epoch_name else timeseries.name
        self._timeseries[name] = EpochTimeSeries(timeseries,
                                                self.start_time,
                                                self.stop_time,
                                                name=name,
                                                parent=self)
        return self._timeseries[name]


@register_class('EpochTimeSeries', CORE_NAMESPACE)
class EpochTimeSeries(NWBContainer):
    __nwbfields__ = ('name',
                     'count',
                     'idx_start',
                     'timeseries')

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'ts', 'type': TimeSeries, 'doc':'the TimeSeries object'},
            {'name': 'start_time', 'type': float, 'doc':'the start time of the epoch'},
            {'name': 'stop_time', 'type': float, 'doc':'the stop time of the epoch'},
            {'name': 'name', 'type': str, 'doc':'the name of this alignment', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        pargs, pkwargs = fmt_docval_args(super().__init__, kwargs)
        ts, start_time, stop_time, parent = getargs('ts', 'start_time', 'stop_time', 'parent', kwargs)
        pkwargs.setdefault('name', ts.name)
        super().__init__(*pargs, **pkwargs)
        self.timeseries = ts
        if ts.starting_time is not None and ts.rate is not None:
            start_idx = int((start_time - ts.starting_time)*ts.rate)
            stop_idx = int((stop_time - ts.starting_time)*ts.rate)
        elif len(ts.timestamps) > 0:
            timestamps = ts.timestamps
            #XXX This assume timestamps are sorted!
            start_idx = bisect_left(timestamps, start_time)
            stop_idx = bisect_left(timestamps, stop_time)
            #TODO: check to see if this should be inclusive or exclusive
            # assume exclusive for now - AJT 10/24/16
        else:
            raise ValueError("TimeSeries object must have timestamps or starting_time and rate")
        self.count = stop_idx - start_idx
        self.idx_start = start_idx



