from ..form.build import ObjectMapper, RegionBuilder
from .. import register_map

from pynwb.core import NWBData, DynamicTable


@register_map(DynamicTable)
class DynamicTableMap(ObjectMapper):

    def __init__(self, spec):
        super(DynamicTableMap, self).__init__(spec)
        columns_spec = spec.get_neurodata_type('TableColumn')
        self.map_spec('columns', columns_spec)

    @ObjectMapper.object_attr('colnames')
    def attr_columns(self, container, manager):
        if all(len(col) == 0 for col in container.columns):
            return tuple()
        return container.colnames


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
