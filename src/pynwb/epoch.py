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

    __col_desc = {
        'start_time': 'Start time of epoch, in seconds',
        'stop_time': 'Stop time of epoch, in seconds',
        'tags': 'user-defined tags',
        'timeseries': 'index into a TimeSeries object'

    }

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeIntervals',
             'default': "experimental intervals"},
            {'name': 'name', 'type': str, 'doc': 'name of this TimeIntervals', 'default': 'epochs'},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers), 'doc': 'the identifiers for this table',
             'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
            'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(TimeIntervals, self).__init__, kwargs)
        self.__has_timeseries = False
        self.__has_tags = False
        if len(self.colnames) == 0:
            self.add_column(name='start_time', description=self.__col_desc['start_time'])
            self.add_column(name='stop_time', description=self.__col_desc['stop_time'])
            if 'tags' in self.colnames:
                self.__has_tags = True
            if 'timeseries' in self.colnames:
                self.__has_timeseries = True

    def __check_tags(self):
        if not self.__has_tags:
            self.add_vector_column(name='tags', description=self.__col_desc['tags'])
            self.__has_tags = True

    def __check_timeseries(self):
        if not self.__has_timeseries:
            self.add_vector_column(name='timeseries', description=self.__col_desc['timeseries'])
            self.__has_timeseries = True

    @docval({'name': 'start_time', 'type': float, 'doc': 'Start time of epoch, in seconds'},
            {'name': 'stop_time', 'type': float, 'doc': 'Stop time of epoch, in seconds'},
            {'name': 'tags', 'type': (str, list, tuple), 'doc': 'user-defined tags uesd throughout epochs',
             'default': None},
            {'name': 'timeseries', 'type': (list, tuple, TimeSeries), 'doc': 'the TimeSeries this epoch applies to',
             'default': None},
            allow_extra=True)
    def add_epoch(self, **kwargs):
        tags, timeseries = popargs('tags', 'timeseries', kwargs)
        start_time, stop_time = getargs('start_time', 'stop_time', kwargs)
        rkwargs = dict(kwargs)
        if tags is not None:
            self.__check_tags()
            if isinstance(tags, str):
                tags = [s.strip() for s in tags.split(",") if not s.isspace()]
            rkwargs['tags'] = tags
        if not (timeseries is None or (isinstance(timeseries, (tuple, list)) and len(timeseries) == 0)):
            self.__check_timeseries()
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
        {'name': 'source', 'type': str, 'doc': 'a description of where this table came from'},
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
        columns = [
            {'name': 'start_time', 'description': cls.__col_desc['start_time']},
            {'name': 'stop_time', 'description': cls.__col_desc['stop_time']},
            {'name': 'tags', 'description': cls.__col_desc['tags'], 'vector_data': True},
            {'name': 'timeseries', 'description': cls.__col_desc['timeseries'], 'vector_data': True},
        ]
        if tmp_columns is not None:
            for d in tmp_columns:
                if not isinstance(d, dict):
                    raise ValueError("'columns' must be a list/tuple of dictionaries")
                if d['name'] in cls.__col_desc:
                    continue
                columns.append(d)
        pkwargs = dict(kwargs)
        pkwargs['columns'] = columns
        return super(TimeIntervals, cls).from_dataframe(**pkwargs)
