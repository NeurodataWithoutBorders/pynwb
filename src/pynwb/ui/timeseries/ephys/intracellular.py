import numpy as np
from collections import Iterable

from pynwb.core import docval, getargs, popargs
from pynwb.ui.container import NWBContainer, nwbproperties

from ..timeseries import TimeSeries, _default_conversion, _default_resolution

class PatchClampSeries(TimeSeries):
    pass

class CurrentClampSeries(PatchClampSeries):
    pass

class IZeroClampSeries(CurrentClampSeries):
    pass

class CurrentClampStimulusSeries(PatchClampSeries):
    pass

class VoltageClampSeries(PatchClampSeries):
    pass

class VoltageClampStimulusSeries(PatchClampSeries):
    pass

