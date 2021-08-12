from bisect import bisect_left

from hdmf.utils import docval, getargs, popargs, call_docval_func, get_docval
from hdmf.data_utils import DataIO

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, TimeSeriesReferenceVectorData, TimeSeriesReference
from hdmf.common import DynamicTable


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
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        # Migrating the timeseries column from VectorData to TimeSeriesVectorData.
        # For NWB 2.4 and earlier, the timeseries column was a regular VectorData.
        # The following code migrates the column to a TimeSeriesReferenceVectorData to make
        # the new functionality accessible to older files and keep the interface consistent
        # across file versions. We do the migration by updating the column directly in the
        # 'columns' argument so that we already have the correct type when calling the
        # __init__ of DynamicTable and avoid issues of bad column types there.
        cols = getargs('columns', kwargs)
        self.__timeseries_column_type_migrated = False
        if cols is not None:
            for c in cols:
                if c.name == 'timeseries':
                    # since the self.timeseries VectorData has the same schema and
                    # memory layout as TimeSeriesReferenceVectorData we can
                    # simply swap out the class to get access to the added functionality
                    # from TimeSeriesReferenceVectorData for old files
                    c.__class__ = TimeSeriesReferenceVectorData
                    self.__timeseries_column_type_migrated = True
        # Call the super constructor
        call_docval_func(super(TimeIntervals, self).__init__, kwargs)

    @property
    def timeseries_column_type_migrated(self):
        """
        Check whether the :py:meth:`~pynwb.epoch.TimeIntervals.timeseries` column has been automatically migrated
        from a regular :py:class:`~hdmf.common.table.VectorData` to a
        :py:class:`~pynwb.base.TimeSeriesReferenceVectorData`
        """
        return self.__timeseries_column_type_migrated

    @docval({'name': 'start_time', 'type': 'float', 'doc': 'Start time of epoch, in seconds'},
            {'name': 'stop_time', 'type': 'float', 'doc': 'Stop time of epoch, in seconds'},
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
        return super(TimeIntervals, self).add_row(**rkwargs)

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
        if ts_starting_time is not None and ts_rate:
            start_idx = int((start_time - ts_starting_time)*ts_rate)
            stop_idx = int((stop_time - ts_starting_time)*ts_rate)
        elif len(ts_timestamps) > 0:
            timestamps = ts_timestamps
            start_idx = bisect_left(timestamps, start_time)
            stop_idx = bisect_left(timestamps, stop_time)
        else:
            raise ValueError("TimeSeries object must have timestamps or starting_time and rate")
        count = stop_idx - start_idx
        idx_start = start_idx
        return int(idx_start), int(count)
