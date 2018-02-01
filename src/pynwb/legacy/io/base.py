from pynwb.base import TimeSeries, ProcessingModule

from .. import ObjectMapper, register_map

legacy_TimeSeries_missing_time_info_name_list = ('natural_movie_one_image_stack',
                                                 'natural_movie_two_image_stack',
                                                 'natural_movie_three_image_stack',
                                                 'natural_scenes_image_stack',
                                                 'locally_sparse_noise_image_stack',
                                                 'locally_sparse_noise_8deg_image_stack',
                                                 'locally_sparse_noise_4deg_image_stack')


@register_map(ProcessingModule)
class ModuleMap(ObjectMapper):

    def __init__(self, spec):
        super(ModuleMap, self).__init__(spec)
        containers_spec = self.spec.get_neurodata_type('NWBDataInterface')
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
        # self.map_attr('interval', timestamps_spec.get_attribute('interval'))
        starting_time_spec = self.spec.get_dataset('starting_time')
        self.map_attr('rate_unit', starting_time_spec.get_attribute('unit'))
        self.map_attr('rate', starting_time_spec.get_attribute('rate'))

    @ObjectMapper.constructor_arg('name')
    def carg_name(self, *args):
        builder = args[0]
        return builder.name

    @ObjectMapper.constructor_arg('starting_time')
    def carg_starting_time(self, *args):
        builder = args[0]
        if builder.name in legacy_TimeSeries_missing_time_info_name_list:
            return -1.0

    @ObjectMapper.constructor_arg('rate')
    def carg_rate(self, *args):
        builder = args[0]
        if builder.name in legacy_TimeSeries_missing_time_info_name_list:
            return -1.0
