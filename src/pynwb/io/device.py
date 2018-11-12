from .. import register_map
from .core import NWBContainerMap

from pynwb.device import Device


@register_map(Device)
class DeviceMap(NWBContainerMap):

    @NWBContainerMap.constructor_arg('description')
    def carg_description(self, builder, manager):
        ret = builder.get('description')
        if ret is None:
            ret = "no description found in file"
        return ret
