from .. import register_map

from pynwb.epoch import EpochTable
from .core import DynamicTableMap


@register_map(EpochTable)
class EpochTableMap(DynamicTableMap):
    pass
