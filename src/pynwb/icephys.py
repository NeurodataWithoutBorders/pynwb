from .base import TimeSeries
from .core import docval, getargs, NWBContainer

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

class IntracellularElectrode(NWBContainer):
    # see /general/intracellular_ephys/<electrode_X> spec
    pass
