from ..form.utils import docval, getargs
from ..form.build import ObjectMapper, RegionBuilder, BuildManager
from ..form.spec import Spec
from ..form.container import Container
from .. import register_map

from pynwb.core import NWBData, DynamicTable


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


@register_map(NWBData)
class NWBDataMap(ObjectMapper):

    @ObjectMapper.constructor_arg('name')
    def carg_name(self, builder, manager):
        return builder.name

    @ObjectMapper.constructor_arg('data')
    def carg_data(self, builder, manager):
        return builder.data


class NWBTableRegionMap(NWBDataMap):

    @ObjectMapper.constructor_arg('table')
    def carg_table(self, builder, manager):
        return manager.construct(builder.data.builder)

    @ObjectMapper.constructor_arg('region')
    def carg_region(self, builder, manager):
        if not isinstance(builder.data, RegionBuilder):
            raise ValueError("'builder' must be a RegionBuilder")
        return builder.data.region
