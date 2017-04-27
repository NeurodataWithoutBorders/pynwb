from .base import TimeSeries, _default_resolution, _default_conversion
from .utils import docval, popargs
from .core import NWBContainer

import numpy as np
from collections import Iterable


class PatchClampSeries(TimeSeries):
    '''
    Stores stimulus or response current or voltage. Superclass definition for patch-clamp data
    (this class should not be instantiated directly).
    '''

    __nwbfields__ = ('electrode_name',
                     'gain')

    _ancestry = "TimeSeries,PatchClampSeries"
    _help = "Superclass definition for patch-clamp data."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        super(PatchClampSeries, self).__init__(name, source, data, unit, **kwargs)
        self.electrode_name = electrode_name
        self.gain = gain

class CurrentClampSeries(PatchClampSeries):
    '''
    Stores voltage data recorded from intracellular current-clamp recordings. A corresponding
    CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current
    injected.
    '''

    __nwbfields__ = ('bias_current',
                     'bridge_balance',
                     'capacitance_compensation')

    _ancestry = "TimeSeries,PatchClampSeries,CurrentClampSeries"
    _help = "Voltage recorded from cell during current-clamprecording."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'bias_current', 'type': float, 'doc': 'Unit: Amp'},
            {'name': 'bridge_balance', 'type': float, 'doc': 'Unit: Ohm'},
            {'name': 'capacitance_compensation', 'type': float, 'doc': 'Unit: Farad'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        bias_current, bridge_balance, capacitance_compensation = popargs('bias_current', 'bridge_balance', 'capacitance_compensation', kwargs)
        super(CurrentClampSeries, self).__init__(name, source, data, unit, electrode_name, gain, **kwargs)
        self.bias_current = bias_current
        self.bridge_balance = bridge_balance
        self.capacitance_compensation = capacitance_compensation

class IZeroClampSeries(CurrentClampSeries):
    '''
    Stores recorded voltage data from intracellular recordings when all current and amplifier settings
    are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries
    associated with an IZero series because the amplifier is disconnected and no stimulus can reach
    the cell.
    '''

    __nwbfields__ = ()

    _ancestry = "TimeSeries,PatchClampSeries,CurrentClampSeries,IZeroClampSeries"
    _help = "Voltage from intracellular recordings when all current and amplifier settings are off,"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'bias_current', 'type': float, 'doc': 'Unit: Amp', 'default': 0.0},
            {'name': 'bridge_balance', 'type': float, 'doc': 'Unit: Ohm', 'default': 0.0},
            {'name': 'capacitance_compensation', 'type': float, 'doc': 'Unit: Farad', 'default': 0.0},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        bias_current, bridge_balance, capacitance_compensation = popargs('bias_current', 'bridge_balance', 'capacitance_compensation', kwargs)
        super(IZeroClampSeries, self).__init__(name, source, data, unit, electrode_name, gain, bias_current, bridge_balance, capacitance_compensation, **kwargs)


class CurrentClampStimulusSeries(PatchClampSeries):
    '''
    Aliases to standard PatchClampSeries. Its functionality is to better tag PatchClampSeries for
    machine (and human) readability of the file.
    '''

    __nwbfields__ = ()

    _ancestry = "TimeSeries,PatchClampSeries,CurrentClampStimulusSeries"
    _help = "Stimulus current applied during current clamp recording."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        super(CurrentClampStimulusSeries, self).__init__(name, source, data, unit, electrode_name, gain, **kwargs)

class VoltageClampSeries(PatchClampSeries):
    '''
    Stores current data recorded from intracellular voltage-clamp recordings. A corresponding
    VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage
    injected.
    '''

    __nwbfields__ = ('capacitance_fast',
                     'capacitance_slow',
                     'resistance_comp_bandwidth',
                     'resistance_comp_correction',
                     'resistance_comp_prediction',
                     'whole_cell_capacitance_comp',
                     'whole_cell_series_resistance_comp')

    _ancestry = "TimeSeries,PatchClampSeries,VoltageClampSeries"
    _help = "Current recorded from cell during voltage-clamp recording"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'capacitance_fast', 'type': float, 'doc': 'Unit: Farad'},
            {'name': 'capacitance_slow', 'type': float, 'doc': 'Unit: Farad'},
            {'name': 'resistance_comp_bandwidth', 'type': float, 'doc': 'Unit: Hz'},
            {'name': 'resistance_comp_correction', 'type': float, 'doc': 'Unit: %'},
            {'name': 'resistance_comp_prediction', 'type': float, 'doc': 'Unit: %'},
            {'name': 'whole_cell_capacitance_comp', 'type': float, 'doc': 'Unit: Farad'},
            {'name': 'whole_cell_series_resistance_comp', 'type': float, 'doc': 'Unit: Ohm'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        capacitance_fast, capacitance_slow, resistance_comp_bandwidth, resistance_comp_correction, resistance_comp_prediction, whole_cell_capacitance_comp, whole_cell_series_resistance_comp = popargs('capacitance_fast', 'capacitance_slow', 'resistance_comp_bandwidth', 'resistance_comp_correction', 'resistance_comp_prediction', 'whole_cell_capacitance_comp', 'whole_cell_series_resistance_comp', kwargs)
        super(VoltageClampSeries, self).__init__(name, source, data, unit, electrode_name, gain, **kwargs)
        self.capacitance_fast = capacitance_fast
        self.capacitance_slow = capacitance_slow
        self.resistance_comp_bandwidth = resistance_comp_bandwidth
        self.resistance_comp_correction = resistance_comp_correction
        self.resistance_comp_prediction = resistance_comp_prediction
        self.whole_cell_capacitance_comp = whole_cell_capacitance_comp
        self.whole_cell_series_resistance_comp = whole_cell_series_resistance_comp

class VoltageClampStimulusSeries(PatchClampSeries):
    '''
    Aliases to standard PatchClampSeries. Its functionality is to better tag PatchClampSeries for
    machine (and human) readability of the file.
    '''

    __nwbfields__ = ()

    _ancestry = "TimeSeries,PatchClampSeries,VoltageClampStimulusSeries"
    _help = "Stimulus voltage applied during voltage clamp recording."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'electrode_name', 'type': str, 'doc': 'Name of electrode entry in /general/intracellular_ephys.'},
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        electrode_name, gain = popargs('electrode_name', 'gain', kwargs)
        super(VoltageClampStimulusSeries, self).__init__(name, source, data, unit, electrode_name, gain, **kwargs)

class IntracellularElectrode(NWBContainer):
    # see /general/intracellular_ephys/<electrode_X> spec
    pass

