from ..form.utils import docval, getargs
from ..form.build import BuildManager
from ..form.spec import Spec
from ..form.container import Container

from ..form.build import ObjectMapper
from .. import register_map

from ..base import TimeSeries, ProcessingModule, DynamicTable


@register_map(ProcessingModule)
class ModuleMap(ObjectMapper):

    def __init__(self, spec):
        super(ModuleMap, self).__init__(spec)
        containers_spec = self.spec.get_neurodata_type('NWBDataInterface')
        self.map_spec('data_interfaces', containers_spec)

    @ObjectMapper.constructor_arg('name')
    def name(self, builder, manager):
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
        # self.map_attr('interval', timestamps_spec.get_attribute('interval'))
        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_attr('starting_time_unit', startingtime_spec.get_attribute('unit'))
        self.map_attr('rate', startingtime_spec.get_attribute('rate'))

    @ObjectMapper.constructor_arg('name')
    def name(self, builder, manager):
        return builder.name


@register_map(DynamicTable)
class DynamicTableMap(ObjectMapper):

    def __init__(self, spec):
        super(DynamicTableMap, self).__init__(spec)
        columns_spec = spec.get_neurodata_type('TableColumn')
        self.map_spec('columns', columns_spec)
        vector_data_spec = spec.get_neurodata_type('VectorData')
        vector_index_spec = spec.get_neurodata_type('VectorIndex')
        self.map_spec('columns', vector_data_spec)
        self.map_spec('columns', vector_index_spec)

    @ObjectMapper.object_attr('colnames')
    def attr_columns(self, container, manager):
        if all(len(col) == 0 for col in container.columns):
            return tuple()
        return container.colnames

    @docval({"name": "spec", "type": Spec, "doc": "the spec to get the attribute value for"},
            {"name": "container", "type": Container, "doc": "the container to get the attribute value from"},
            {"name": "manager", "type": BuildManager, "doc": "the BuildManager used for managing this build"},
            returns='the value of the attribute')
    def get_attr_value(self, **kwargs):
        ''' Get the value of the attribute corresponding to this spec from the given container '''
        spec, container, manager = getargs('spec', 'container', 'manager', kwargs)
        attr_value = super(DynamicTableMap, self).get_attr_value(spec, container, manager)
        if attr_value is None and spec.name in container:
            if spec.neurodata_type_inc == 'TableColumn':
                attr_value = container[spec.name]
            elif spec.neurodata_type_inc == 'VectorData':
                attr_value = container[spec.name].target
        return attr_value
