from pynwb.core import docval, getargs, popargs

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
