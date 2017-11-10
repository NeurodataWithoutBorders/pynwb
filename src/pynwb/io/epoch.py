from ..form.build import ObjectMapper
from .. import register_map

from pynwb.epoch import Epoch, EpochTimeSeries


@register_map(Epoch)
class EpochMap(ObjectMapper):

    def __init__(self, spec):
        super(EpochMap, self).__init__(spec)
        start_spec = self.spec.get_dataset('start_time')
        stop_spec = self.spec.get_dataset('stop_time')
        self.map_const_arg('start', start_spec)
        self.map_const_arg('stop', stop_spec)
        epts_spec = self.spec.get_neurodata_type('EpochTimeSeries')
        self.map_spec('timeseries', epts_spec)

    @ObjectMapper.constructor_arg('name')
    def name(self, builder, manager):
        return builder.name


@register_map(EpochTimeSeries)
class EpochTimeSeriesMap(ObjectMapper):

    def __init__(self, spec):
        super(EpochTimeSeriesMap, self).__init__(spec)
        ts_spec = self.spec.get_link('timeseries')
        self.map_const_arg('ts', ts_spec)
