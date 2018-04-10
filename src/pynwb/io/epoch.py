from .. import register_map

from pynwb.epoch import EpochTable, TimeSeriesIndex, EpochTableRegion
from .core import NWBDataMap, NWBTableRegionMap


@register_map(EpochTable)
class EpochTableMap(NWBDataMap):
    pass


@register_map(TimeSeriesIndex)
class TimeSeriesIndexMap(NWBDataMap):
    pass


@register_map(EpochTableRegion)
class EpochTableRegionMap(NWBTableRegionMap):
    pass
