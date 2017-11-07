from .. import register_map

from ..ecephys import ElectrodeTable, ElectrodeTableRegion
from .core import NWBDataMap, NWBTableRegionMap


@register_map(ElectrodeTable)
class ElectrodeTableMap(NWBDataMap):
    def __init__(self, spec):
        super(ElectrodeTableMap, self).__init__(spec)


@register_map(ElectrodeTableRegion)
class ElectrodeTableRegionMap(NWBTableRegionMap):
    pass
