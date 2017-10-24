from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.base import TimeSeries, ProcessingModule

@register_map(ProcessingModule)
class ModuleMap(ObjectMapper):

    def __init__(self, spec):
        super(ModuleMap, self).__init__(spec)
        containers_spec = self.spec.get_neurodata_type('NWBContainer')
        self.map_spec('containers', containers_spec)

    @ObjectMapper.constructor_arg('name')
    def name(self, *args):
        builder = args[0]
        return builder.name

    @ObjectMapper.constructor_arg('description')
    def carg_description(self, *args):
        return 'Brain Observatory Processing Module'


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
    def carg_name(self, *args):
        builder = args[0]
        return builder.name

    @ObjectMapper.constructor_arg('starting_time')
    def carg_starting_time(self, *args):
        builder = args[0]
        if builder.name in ('natural_movie_one_image_stack', 'natural_scenes_image_stack'):
            return -1.0

    @ObjectMapper.constructor_arg('rate')
    def carg_rate(self, *args):
        builder = args[0]
        if builder.name in ('natural_movie_one_image_stack', 'natural_scenes_image_stack'):
            return -1.0

    # @ObjectMapper.constructor_arg('data')
    # def carg_data(self, *args):
    #     builder = args[0]
    #     manager = args[1]
    #     if builder.name in ('corrected',):
    #         return np.array([])
    #     else:
            
    #         subspecs = self.hack_get_subspec_values(builder, self.spec, manager)
    #         for subspec, value in subspecs.items():
    #             const_arg = self.get_const_arg(subspec)
    #             if const_arg == 'data':
    #                 return value


            # builder.datasets['data']['data']

    # def __get_override_carg(self, *args, **kwargs):
    #     return self.hack_get_override_carg(*args, **kwargs)