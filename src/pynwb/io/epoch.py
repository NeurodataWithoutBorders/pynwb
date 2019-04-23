from .. import register_map

from pynwb.epoch import TimeIntervals, TimeSeriesIndex
from .core import DynamicTableMap, VectorIndex


@register_map(TimeIntervals)
class TimeIntervalsMap(DynamicTableMap):

    @DynamicTableMap.constructor_arg('columns')
    def construct_columns(self, builder, manager):
        ret = list()
        for colbuilder in builder.datasets.values():
            if colbuilder.attributes.get('neurodata_type') not in ('VectorData', 'VectorIndex'):
                continue
            if colbuilder.name in ('timeseries', 'timeseries_index'):
                continue
            else:
                ret.append(manager.construct(colbuilder))
        ts_builder = builder.datasets['timeseries']
        tsidx_builder = builder.datasets['timeseries_index']
        ts = TimeSeriesIndex(name='timeseries', data=ts_builder.data, description=ts_builder.attributes['description'])
        tsidx = VectorIndex(name='timseries_index', data=tsidx_builder.data, target=ts)
        manager.prebuilt(tsidx, tsidx_builder)
        manager.prebuilt(ts, ts_builder)
        ret.append(ts)
        ret.append(tsidx)
        return ret
