from .. import register_map

from pynwb.epoch import TimeIntervals
from .core import DynamicTableMap


@register_map(TimeIntervals)
class TimeIntervalsMap(DynamicTableMap):
    pass
