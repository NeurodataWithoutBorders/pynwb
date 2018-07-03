from bisect import bisect_left

from .form.utils import docval, getargs, popargs, call_docval_func, get_docval
from .form.data_utils import DataIO, RegionSlicer
from .form import get_region_slicer

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import NWBContainer, NWBTable, NWBTableRegion, DynamicTable


_evtable_docval = [
    {'name': 'start_time', 'type': float, 'doc': 'Start time of epoch, in seconds'},
    {'name': 'stop_time', 'type': float, 'doc': 'Stop time of epoch, in seconds'},
    {'name': 'tags', 'type': (str, list, tuple), 'doc': 'user-defined tags uesd throughout epochs'},
    {'name': 'timeseries', 'type': RegionSlicer, 'doc': 'the TimeSeries the epoch applies to'},
]


@register_class('EpochTable', CORE_NAMESPACE)
class EventTable(NWBTable):

    __columns__ = _evtable_docval


_eptable_docval = _evtable_docval + [
    {'name': 'description', 'type': str, 'doc': 'a description of this epoch'},
]


@register_class('EpochTable', CORE_NAMESPACE)
class EpochTable(NWBTable):

    __columns__ = _eptable_docval

    __defaultname__ = 'epochs'


@register_class('EpochTableRegion', CORE_NAMESPACE)
class EpochTableRegion(NWBTableRegion):
    '''A subsetting of an EpochTable'''

    __nwbfields__ = ('description',)

    @docval({'name': 'table', 'type': EpochTable, 'doc': 'the EpochTable this region applies to'},
            {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what this subset of epochs is'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'epochs'})
    def __init__(self, **kwargs):
        call_docval_func(super(EpochTableRegion, self).__init__, kwargs)
        self.description = getargs('description', kwargs)


_tsi_docval = [
    {'name': 'idx_start', 'type': int, 'doc': 'start index into the TimeSeries.data field'},
    {'name': 'count', 'type': int, 'doc': 'number of data samples available in this TimeSeries'},
    {'name': 'timeseries', 'type': TimeSeries, 'doc': 'the TimeSeries object this index applies to'},
]


@register_class('TimeSeriesIndex', CORE_NAMESPACE)
class TimeSeriesIndex(NWBTable):

    __columns__ = _tsi_docval

    __defaultname__ = 'timeseries_index'


@register_class('Epochs', CORE_NAMESPACE)
class Epochs(NWBContainer):

    __nwbfields__ = (
            {'name': 'epochs', 'child': True},
            {'name': 'timeseries_index', 'child': True},
            {'name': 'metadata', 'child': True}
    )

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'name', 'type': str, 'doc': 'the name of this epoch table', 'default': 'epochs'},
            {'name': 'epochs', 'type': EpochTable, 'doc': 'the EpochTable holding information about each epoch',
             'default': None},
            {'name': 'timeseries_index', 'type': TimeSeriesIndex,
             'doc': 'the TimeSeriesIndex table holding indices into each TimeSeries for each epoch', 'default': None},
            {'name': 'metadata', 'type': DynamicTable, 'doc': 'a metadata table for the epochs',
             'default': None})
    def __init__(self, **kwargs):
        epochs, timeseries_index, metadata = popargs('epochs', 'timeseries_index', 'metadata', kwargs)
        call_docval_func(super(Epochs, self).__init__, kwargs)
        self.epochs = epochs if epochs is not None else EpochTable()
        self.timeseries_index = timeseries_index if timeseries_index else TimeSeriesIndex()
        if metadata is not None:
            self.metadata = metadata

    def __check_metadata(self):
        if self.metadata is None:
            self.metadata = DynamicTable('metadata', self.source, 'a table for metadata about each epoch')

    @docval({'name': 'description', 'type': str, 'doc': 'a description of this epoch'},
            {'name': 'start_time', 'type': float, 'doc': 'Start time of epoch, in seconds'},
            {'name': 'stop_time', 'type': float, 'doc': 'Stop time of epoch, in seconds'},
            {'name': 'tags', 'type': (str, list, tuple), 'doc': 'user-defined tags uesd throughout epochs'},
            {'name': 'timeseries', 'type': (list, tuple, TimeSeries), 'doc': 'the TimeSeries this epoch applies to'},
            {'name': 'metadata', 'type': dict, 'doc': 'the metadata about this epoch', 'default': None})
    def add_epoch(self, **kwargs):
        description, start_time, stop_time, tags, timeseries, metadata =\
            getargs('description', 'start_time', 'stop_time', 'tags', 'timeseries', 'metadata', kwargs)
        if isinstance(timeseries, TimeSeries):
            timeseries = [timeseries]
        n_tsi = len(self.timeseries_index)
        n_ts = len(timeseries)
        for ts in timeseries:
            idx_start, count = self.__calculate_idx_count(start_time, stop_time, ts)
            self.timeseries_index.add_row(idx_start, count, ts)
        tsi_region = get_region_slicer(self.timeseries_index, slice(n_tsi, n_tsi+n_ts))
        if isinstance(tags, (tuple, list)):
            tags = ",".join(tags)
        self.epochs.add_row(start_time, stop_time, tags, tsi_region, description)
        if metadata is None:
            if self.metadata is not None:
                raise ValueError("must consistently provide metdata for epochs")
        else:
            self.__check_metadata()
            if len(self.metadata) != len(self.epochs) - 1:
                raise ValueError("must consistently provide metdata for epochs")
            self.metadata.add_row(metadata)

    @docval(*get_docval(DynamicTable.add_column))
    def add_metadata_column(self, **kwargs):
        """
        Add a column to the trial table. See DynamicTable.add_column for more details
        """
        self.__check_metadata()
        if len(self.epochs) > 0 or len(self.metadata) > 0:
            raise ValueError("cannot add columns after table has been populated")
        call_docval_func(self.metadata.add_column, kwargs)

    def get_timeseries(self, epoch_idx, ts_name):
        ep_row = self.epochs[epoch_idx]
        for tsi in ep_row[3]:
            if tsi[2].name == ts_name:
                timestamps = tsi[2].timestamps[tsi[0]:tsi[0]+tsi[1]]
                data = tsi[2].data[tsi[0]:tsi[0]+tsi[1]]
                return (data, timestamps)
        return (None, None)

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
