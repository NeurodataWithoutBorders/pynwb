from bisect import bisect_left

from .form.utils import docval, getargs, popargs, call_docval_func
from .form.data_utils import DataIO

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import DynamicTable, ElementIdentifiers

import pandas as pd


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
        {'name': 'timeseries', 'description': 'index into a TimeSeries object', 'index': True}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this TimeIntervals'},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeIntervals',
             'default': "experimental intervals"},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers), 'doc': 'the identifiers for this table',
             'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
            'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(TimeIntervals, self).__init__, kwargs)

    @docval({'name': 'start_time', 'type': float, 'doc': 'Start time of epoch, in seconds'},
            {'name': 'stop_time', 'type': float, 'doc': 'Stop time of epoch, in seconds'},
            {'name': 'tags', 'type': (str, list, tuple), 'doc': 'user-defined tags uesd throughout epochs',
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
                tmp.append((idx_start, count, ts))
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
        return (int(idx_start), int(count))

    @classmethod
    @docval(
        {'name': 'df', 'type': pd.DataFrame, 'doc': 'source DataFrame'},
        {'name': 'name', 'type': str, 'doc': 'the name of this table'},
        {
            'name': 'index_column',
            'type': str,
            'help': 'if provided, this column will become the table\'s index',
            'default': None
        },
        {
            'name': 'table_description',
            'type': str,
            'help': 'a description of what is in the resulting table',
            'default': ''
        },
        {
            'name': 'columns',
            'type': (list, tuple),
            'help': 'a list/tuple of dictionaries specifying columns in the table',
            'default': None
        },
        allow_extra=True
    )
    def from_dataframe(cls, **kwargs):
        '''Construct an instance of DynamicTable (or a subclass) from a pandas DataFrame. The columns of the resulting
        table are defined by the columns of the dataframe and the index by the dataframe's index (make sure it has a
        name!) or by a column whose name is supplied to the index_column parameter. We recommend that you supply
        column_descriptions - a dictionary mapping column names to string descriptions - to help others understand
        the contents of your table.
        '''
        tmp_columns = popargs('columns', kwargs)
        columns = list(cls.__columns__)
        if tmp_columns is not None:
            exist = {c['name'] for c in columns}
            for d in tmp_columns:
                if not isinstance(d, dict):
                    raise ValueError("'columns' must be a list/tuple of dictionaries")
                if d['name'] in exist:
                    msg = "cannot override specification for column '%s'" % d['name']
                    raise ValueError(msg)
                columns.append(d)
        pkwargs = dict(kwargs)
        pkwargs['columns'] = columns
        return super(TimeIntervals, cls).from_dataframe(**pkwargs)
