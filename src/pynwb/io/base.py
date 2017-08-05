from form.build import ObjectMapper
from .. import register_map

from ..base import TimeSeries, Module

@register_map(Module)
class ModuleMap(ObjectMapper):

    def __init__(self, spec):
        super(ModuleMap, self).__init__(spec)
        interfaces_spec = self.spec.get_neurodata_type('Interface')
        self.map_spec('interfaces', interfaces_spec)
        self.map_spec('interface_names', self.spec.get_attribute('interfaces'))

    @ObjectMapper.constructor_arg('name')
    def name(self, builder):
        return builder.name

@register_map(TimeSeries)
class TimeSeriesMap(ObjectMapper):

    def __init__(self, spec):
        super(TimeSeriesMap, self).__init__(spec)
        data_spec = self.spec.get_dataset('data')
        self.map_attr('unit', data_spec.get_attribute('unit'))
        self.map_const_arg('unit', data_spec.get_attribute('unit'))
        self.map_attr('resolution', data_spec.get_attribute('resolution'))
        self.map_attr('conversion', data_spec.get_attribute('conversion'))
        timestamps_spec = self.spec.get_dataset('timestamps')
        self.map_attr('timestamps_unit', timestamps_spec.get_attribute('unit'))
        #self.map_attr('interval', timestamps_spec.get_attribute('interval'))
        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_attr('rate_unit', startingtime_spec.get_attribute('unit'))
        self.map_attr('rate', startingtime_spec.get_attribute('rate'))

    @ObjectMapper.constructor_arg('name')
    def name(self, builder):
        return builder.name
