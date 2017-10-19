from form.build import ObjectMapper, RegionBuilder
from .. import register_map

from pynwb.core import NWBData, NWBTableRegion

@register_map(NWBData)
class NWBDataMapper(ObjectMapper):

    @ObjectMapper.constructor_arg('name')
    def carg_name(self, builder, manager):
        return builder.name

class NWBTableRegionMap(NWBDataMapper):

    @ObjectMapper.constructor_arg('table')
    def carg_table(self, builder, manager):
        return manager.construct(builder.data)

    @ObjectMapper.constructor_arg('region')
    def carg_region(self, builder, manager):
        if not isinstance(builder, RegionBuilder):
            raise ValueError("'builder' must be a RegionBuilder")
        return builder.region
