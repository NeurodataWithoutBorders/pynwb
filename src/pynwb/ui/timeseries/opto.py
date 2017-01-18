import numpy as np
from collections import Iterable

from pynwb.core import docval, getargs, popargs
from ..container import NWBContainer, nwbproperties

from .timeseries import TimeSeries, _default_conversion, _default_resolution

class OptogeneticSeries(TimeSeries):
    def set_data(self, data, conversion=None, resolution=None):
        super().set_data(data, "watt", conversion=conversion, resolution=resolution)
