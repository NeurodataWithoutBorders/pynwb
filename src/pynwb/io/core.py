from hdmf.build import ObjectMapper, RegionBuilder
from hdmf.common import VectorData
from hdmf.utils import getargs, docval
from hdmf.spec import AttributeSpec
from hdmf.build import BuildManager

from .. import register_map

from pynwb.file import NWBFile
from pynwb.core import NWBData, NWBContainer
from pynwb.misc import Units


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


@register_map(VectorData)
class VectorDataMap(ObjectMapper):

    @docval({"name": "spec", "type": AttributeSpec, "doc": "the spec to get the attribute value for"},
            {"name": "container", "type": VectorData, "doc": "the container to get the attribute value from"},
            {"name": "manager", "type": BuildManager, "doc": "the BuildManager used for managing this build"},
            returns='the value of the attribute')
    def get_attr_value(self, **kwargs):
        ''' Get the value of the attribute corresponding to this spec from the given container '''
        spec, container, manager = getargs('spec', 'container', 'manager', kwargs)

        # handle custom mapping of container Units.waveform_rate -> spec Units.waveform_mean.sampling_rate
        if isinstance(container.parent, Units):
            if container.name == 'waveform_mean' or container.name == 'waveform_sd':
                if spec.name == 'sampling_rate':
                    return container.parent.waveform_rate
                if spec.name == 'unit':
                    return container.parent.waveform_unit
            if container.name == 'spike_times':
                if spec.name == 'resolution':
                    return container.parent.resolution
        return super().get_attr_value(**kwargs)
