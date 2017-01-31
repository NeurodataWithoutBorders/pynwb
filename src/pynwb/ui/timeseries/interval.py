import numpy as np
from collections import Iterable

from pynwb.core import docval, getargs, popargs
from ..container import NWBContainer

from .timeseries import TimeSeries, _default_conversion, _default_resolution
        
class IntervalSeries(TimeSeries):
    pass
