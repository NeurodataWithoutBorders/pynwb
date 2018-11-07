from .. import register_map

from pynwb.icephys import SweepTable
from .base import DynamicTableMap


@register_map(SweepTable)
class SweepTableMap(DynamicTableMap):
    pass
