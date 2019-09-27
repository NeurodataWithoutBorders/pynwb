from hdmf.build import ObjectMapper, RegionBuilder

from .. import register_map

from pynwb.file import NWBFile
from pynwb.core import NWBData, NWBContainer


class NWBBaseTypeMapper(ObjectMapper):

    @staticmethod
    def get_nwb_file(container):
        curr = container
        while curr is not None:
            if isinstance(curr, NWBFile):
                return curr
            curr = container.parent


@register_map(NWBContainer)
class NWBContainerMapper(NWBBaseTypeMapper):

    pass


@register_map(NWBData)
class NWBDataMap(NWBBaseTypeMapper):

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
