from bisect import bisect_left

import numpy as np

from hdmf.data_utils import DataIO
from hdmf.common import DynamicTable
from hdmf.utils import docval, getargs, popargs, get_docval, AllowPositional

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, TimeSeriesReferenceVectorData, TimeSeriesReference

__all__ = ['TimeIntervals']

@register_class('TimeIntervals', CORE_NAMESPACE)
class TimeIntervals(DynamicTable):
    """
    Table for storing Epoch data
    """

    __defaultname__ = 'epochs'

    __columns__ = (
        {'name': 'start_time', 'description': 'Start time of epoch, in seconds', 'required': True},
        {'name': 'stop_time', 'description': 'Stop time of epoch, in seconds', 'required': True},
        {'name': 'tags', 'description': 'user-defined tags', 'index': True},
        {'name': 'timeseries', 'description': 'index into a TimeSeries object',
         'index': True, 'class': TimeSeriesReferenceVectorData}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this TimeIntervals'},  # required
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeIntervals',
             'default': "experimental intervals"},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames', 'target_tables', 'meanings_tables'),
            allow_positional=AllowPositional.WARNING,)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @docval({'name': 'start_time', 'type': float, 'doc': 'Start time of epoch, in seconds'},
            {'name': 'stop_time', 'type': float, 'doc': 'Stop time of epoch, in seconds'},
            {'name': 'tags', 'type': (str, list, tuple), 'doc': 'user-defined tags used throughout time intervals',
             'default': None},
            {'name': 'timeseries', 'type': (list, tuple, TimeSeries), 'doc': 'the TimeSeries this epoch applies to',
             'default': None},
            allow_extra=True)
    def add_interval(self, **kwargs):
        tags, timeseries = popargs('tags', 'timeseries', kwargs)
        start_time, stop_time = getargs('start_time', 'stop_time', kwargs)
        rkwargs = dict(kwargs)
        if tags is not None:
            if isinstance(tags, str):
                tags = [s.strip() for s in tags.split(",") if not s.isspace()]
            rkwargs['tags'] = tags
        if not (timeseries is None or (isinstance(timeseries, (tuple, list)) and len(timeseries) == 0)):
            if isinstance(timeseries, TimeSeries):
                timeseries = [timeseries]
            tmp = list()
            for ts in timeseries:
                idx_start, count = self.__calculate_idx_count(start_time, stop_time, ts)
                tmp.append(TimeSeriesReference(idx_start, count, ts))
            timeseries = tmp
            rkwargs['timeseries'] = timeseries
        return super().add_row(**rkwargs)

    def __calculate_idx_count(self, start_time, stop_time, ts_data):
        if isinstance(ts_data.timestamps, DataIO):
            ts_timestamps = ts_data.timestamps.data
            ts_starting_time = ts_data.starting_time
            ts_rate = ts_data.rate
        else:
            ts = ts_data
            ts_timestamps = ts.timestamps
            ts_starting_time = ts.starting_time
            ts_rate = ts.rate
        if ts_starting_time is not None and ts_rate is not None:
            start_idx = int((start_time - ts_starting_time)*ts_rate)
            stop_idx = int((stop_time - ts_starting_time)*ts_rate)
        elif ts_timestamps is not None and len(ts_timestamps) > 0:
            timestamps = ts_timestamps
            start_idx = bisect_left(timestamps, start_time)
            stop_idx = bisect_left(timestamps, stop_time)
        else:
            raise ValueError("TimeSeries object must have timestamps or starting_time and rate")
        count = stop_idx - start_idx
        idx_start = start_idx
        return int(idx_start), int(count)

    def get_starting_time(self):
        """
        Get the earliest start time across all intervals in this TimeIntervals table.

        NaN start times are ignored.

        Returns
        -------
        float or None
            The earliest non-NaN start time in seconds, or None if the table is
            empty or all start times are NaN.
        """
        if len(self) == 0:
            return None
        start_time = np.asarray(self['start_time'].data[:], dtype=float)
        if np.all(np.isnan(start_time)):
            return None
        # NOTE: Could be optimized to self['start_time'].data[0] if intervals are guaranteed sorted
        return float(np.nanmin(start_time))

    def get_duration(self):
        """
        Get the total duration from the earliest start time to the latest stop time.

        Returns
        -------
        float or None
            The duration in seconds, or None if the table is empty. Returns NaN if
            all start times are NaN (the earliest start is undefined). If all stop
            times are NaN but valid start times exist, the duration falls back to
            the span of the start times (latest start minus earliest start).

        Notes
        -----
        The duration represents the time span from the earliest interval start to the
        latest interval stop, not the sum of individual interval durations. NaN
        start/stop times (e.g. for ongoing/unbounded intervals) are ignored.
        """
        if len(self) == 0:
            return None
        starting_time = self.get_starting_time()
        if starting_time is None:
            # all start times are NaN, so the earliest start is undefined
            return float("nan")
        stop_time = np.asarray(self['stop_time'].data[:], dtype=float)
        if np.all(np.isnan(stop_time)):
            # no valid stop times: fall back to the span of the start times
            start_time = np.asarray(self['start_time'].data[:], dtype=float)
            return float(np.nanmax(start_time)) - starting_time
        # NOTE: Could be optimized to self['stop_time'].data[-1] if intervals are guaranteed sorted
        stopping_time = float(np.nanmax(stop_time))
        return stopping_time - starting_time
