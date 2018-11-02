from .. import register_map

from pynwb.epoch import TimeIntervals
from .base import DynamicTableMap


@register_map(TimeIntervals)
class TimeIntervalsMap(DynamicTableMap):
    pass
