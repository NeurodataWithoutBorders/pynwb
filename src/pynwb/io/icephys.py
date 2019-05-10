from .. import register_map

from pynwb.icephys import SweepTable
from .core import DynamicTableMap


@register_map(SweepTable)
class SweepTableMap(DynamicTableMap):
    pass
