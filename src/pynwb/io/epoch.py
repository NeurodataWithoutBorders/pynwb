from .. import register_map

from pynwb.epoch import TimeIntervals
from hdmf.common.io.table import DynamicTableMap


@register_map(TimeIntervals)
class TimeIntervalsMap(DynamicTableMap):
    pass
