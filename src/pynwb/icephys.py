import warnings

from hdmf.common import DynamicTable
from hdmf.utils import docval, popargs, call_docval_func, get_docval

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .core import NWBContainer
from .device import Device


@register_class('IntracellularElectrode', CORE_NAMESPACE)
class IntracellularElectrode(NWBContainer):
    '''
    '''

    __nwbfields__ = ('slice',
                     'seal',
                     'description',
                     'location',
                     'resistance',
                     'filtering',
                     'initial_access_resistance',
                     'device')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'device', 'type': Device, 'doc': 'the device that was used to record from this electrode'},
            {'name': 'description', 'type': str,
             'doc': 'Recording description, description of electrode (e.g.,  whole-cell, sharp, etc) '
                    'COMMENT: Free-form text (can be from Methods)'},
            {'name': 'slice', 'type': str, 'doc': 'Information about slice used for recording.', 'default': None},
            {'name': 'seal', 'type': str, 'doc': 'Information about seal used for recording.', 'default': None},
            {'name': 'location', 'type': str,
             'doc': 'Area, layer, comments on estimation, stereotaxis coordinates (if in vivo, etc).', 'default': None},
            {'name': 'resistance', 'type': str, 'doc': 'Electrode resistance COMMENT: unit: Ohm.', 'default': None},
            {'name': 'filtering', 'type': str, 'doc': 'Electrode specific filtering.', 'default': None},
            {'name': 'initial_access_resistance', 'type': str, 'doc': 'Initial access resistance.', 'default': None},
            )
    def __init__(self, **kwargs):
        slice, seal, description, location, resistance, filtering, initial_access_resistance, device = popargs(
            'slice', 'seal', 'description', 'location', 'resistance',
            'filtering', 'initial_access_resistance', 'device', kwargs)
        call_docval_func(super().__init__, kwargs)
        self.slice = slice
        self.seal = seal
        self.description = description
        self.location = location
        self.resistance = resistance
        self.filtering = filtering
        self.initial_access_resistance = initial_access_resistance
        self.device = device


@register_class('PatchClampSeries', CORE_NAMESPACE)
class PatchClampSeries(TimeSeries):
    '''
    Stores stimulus or response current or voltage. Superclass definition for patch-clamp data
    (this class should not be instantiated directly).
    '''

    __nwbfields__ = ('electrode',
                     'gain',
                     'stimulus_description',
                     'sweep_number')

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),  # required
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},  # required
            {'name': 'electrode', 'type': IntracellularElectrode,  # required
             'doc': 'IntracellularElectrode group that describes the electrode that was used to apply '
                     'or record this data.'},
            {'name': 'gain', 'type': 'float', 'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)'},  # required
            {'name': 'stimulus_description', 'type': str, 'doc': 'the stimulus name/protocol', 'default': "NA"},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'),
            {'name': 'sweep_number', 'type': (int, 'uint32', 'uint64'),
             'doc': 'Sweep number, allows for grouping different PatchClampSeries together '
                    'via the sweep_table', 'default': None})
    def __init__(self, **kwargs):
        name, data, unit, stimulus_description = popargs('name', 'data', 'unit', 'stimulus_description', kwargs)
        electrode, gain, sweep_number = popargs('electrode', 'gain', 'sweep_number', kwargs)
        super().__init__(name, data, unit, **kwargs)
        self.electrode = electrode
        self.gain = gain
        self.stimulus_description = stimulus_description

        if sweep_number is not None:
            if not (sweep_number >= 0):
                raise ValueError("sweep_number must be a non-negative integer")

            self.sweep_number = sweep_number


@register_class('CurrentClampSeries', CORE_NAMESPACE)
class CurrentClampSeries(PatchClampSeries):
    '''
    Stores voltage data recorded from intracellular current-clamp recordings. A corresponding
    CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current
    injected.
    '''

    __nwbfields__ = ('bias_current',
                     'bridge_balance',
                     'capacitance_compensation')

    @docval(*get_docval(PatchClampSeries.__init__, 'name', 'data', 'electrode'),  # required
            {'name': 'gain', 'type': 'float', 'doc': 'Units: Volt/Volt'},
            *get_docval(PatchClampSeries.__init__, 'stimulus_description'),
            {'name': 'bias_current', 'type': 'float', 'doc': 'Unit: Amp', 'default': None},
            {'name': 'bridge_balance', 'type': 'float', 'doc': 'Unit: Ohm', 'default': None},
            {'name': 'capacitance_compensation', 'type': 'float', 'doc': 'Unit: Farad', 'default': None},
            *get_docval(PatchClampSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'sweep_number'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'volts')",
             'default': 'volts'})
    def __init__(self, **kwargs):
        name, data, unit, electrode, gain = popargs('name', 'data', 'unit', 'electrode', 'gain', kwargs)
        unit = ensure_unit(self, name, unit, 'volts', '2.1.0')
        bias_current, bridge_balance, capacitance_compensation = popargs(
            'bias_current', 'bridge_balance', 'capacitance_compensation', kwargs)
        super().__init__(name, data, unit, electrode, gain, **kwargs)
        self.bias_current = bias_current
        self.bridge_balance = bridge_balance
        self.capacitance_compensation = capacitance_compensation


@register_class('IZeroClampSeries', CORE_NAMESPACE)
class IZeroClampSeries(CurrentClampSeries):
    '''
    Stores recorded voltage data from intracellular recordings when all current and amplifier settings
    are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries
    associated with an IZero series because the amplifier is disconnected and no stimulus can reach
    the cell.
    '''

    __nwbfields__ = ()

    @docval(*get_docval(CurrentClampSeries.__init__, 'name', 'data', 'electrode'),  # required
            {'name': 'gain', 'type': 'float', 'doc': 'Units: Volt/Volt'},  # required
            *get_docval(CurrentClampSeries.__init__, 'stimulus_description', 'resolution', 'conversion', 'timestamps',
                        'starting_time', 'rate', 'comments', 'description', 'control', 'control_description',
                        'sweep_number'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'volts')",
             'default': 'volts'})
    def __init__(self, **kwargs):
        name, data, electrode, gain = popargs('name', 'data', 'electrode', 'gain', kwargs)
        bias_current, bridge_balance, capacitance_compensation = (0.0, 0.0, 0.0)
        super().__init__(name, data, electrode, gain, bias_current, bridge_balance, capacitance_compensation,
                         **kwargs)


@register_class('CurrentClampStimulusSeries', CORE_NAMESPACE)
class CurrentClampStimulusSeries(PatchClampSeries):
    '''
    Alias to standard PatchClampSeries. Its functionality is to better tag PatchClampSeries for
    machine (and human) readability of the file.
    '''

    __nwbfields__ = ()

    @docval(*get_docval(PatchClampSeries.__init__, 'name', 'data', 'electrode', 'gain'),  # required
            *get_docval(PatchClampSeries.__init__, 'stimulus_description', 'resolution', 'conversion', 'timestamps',
                        'starting_time', 'rate', 'comments', 'description', 'control', 'control_description',
                        'sweep_number'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'amperes')",
             'default': 'amperes'})
    def __init__(self, **kwargs):
        name, data, unit, electrode, gain = popargs('name', 'data', 'unit', 'electrode', 'gain', kwargs)
        unit = ensure_unit(self, name, unit, 'amperes', '2.1.0')
        super().__init__(name, data, unit, electrode, gain, **kwargs)


@register_class('VoltageClampSeries', CORE_NAMESPACE)
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

    @docval(*get_docval(PatchClampSeries.__init__, 'name', 'data', 'electrode'),  # required
            {'name': 'gain', 'type': 'float', 'doc': 'Units: Volt/Amp'},  # required
            *get_docval(PatchClampSeries.__init__, 'stimulus_description'),
            {'name': 'capacitance_fast', 'type': 'float', 'doc': 'Unit: Farad', 'default': None},
            {'name': 'capacitance_slow', 'type': 'float', 'doc': 'Unit: Farad', 'default': None},
            {'name': 'resistance_comp_bandwidth', 'type': 'float', 'doc': 'Unit: Hz', 'default': None},
            {'name': 'resistance_comp_correction', 'type': 'float', 'doc': 'Unit: percent', 'default': None},
            {'name': 'resistance_comp_prediction', 'type': 'float', 'doc': 'Unit: percent', 'default': None},
            {'name': 'whole_cell_capacitance_comp', 'type': 'float', 'doc': 'Unit: Farad', 'default': None},
            {'name': 'whole_cell_series_resistance_comp', 'type': 'float', 'doc': 'Unit: Ohm', 'default': None},
            *get_docval(PatchClampSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'sweep_number'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'amperes')",
             'default': 'amperes'})
    def __init__(self, **kwargs):
        name, data, unit, electrode, gain = popargs('name', 'data', 'unit', 'electrode', 'gain', kwargs)
        unit = ensure_unit(self, name, unit, 'amperes', '2.1.0')
        capacitance_fast, capacitance_slow, resistance_comp_bandwidth, resistance_comp_correction, \
            resistance_comp_prediction, whole_cell_capacitance_comp, whole_cell_series_resistance_comp = popargs(
                'capacitance_fast', 'capacitance_slow', 'resistance_comp_bandwidth',
                'resistance_comp_correction', 'resistance_comp_prediction', 'whole_cell_capacitance_comp',
                'whole_cell_series_resistance_comp', kwargs)
        super().__init__(name, data, unit, electrode, gain, **kwargs)
        self.capacitance_fast = capacitance_fast
        self.capacitance_slow = capacitance_slow
        self.resistance_comp_bandwidth = resistance_comp_bandwidth
        self.resistance_comp_correction = resistance_comp_correction
        self.resistance_comp_prediction = resistance_comp_prediction
        self.whole_cell_capacitance_comp = whole_cell_capacitance_comp
        self.whole_cell_series_resistance_comp = whole_cell_series_resistance_comp


@register_class('VoltageClampStimulusSeries', CORE_NAMESPACE)
class VoltageClampStimulusSeries(PatchClampSeries):
    '''
    Alias to standard PatchClampSeries. Its functionality is to better tag PatchClampSeries for
    machine (and human) readability of the file.
    '''

    __nwbfields__ = ()

    @docval(*get_docval(PatchClampSeries.__init__, 'name', 'data', 'electrode', 'gain'),  # required
            *get_docval(PatchClampSeries.__init__, 'stimulus_description', 'resolution', 'conversion', 'timestamps',
                        'starting_time', 'rate', 'comments', 'description', 'control', 'control_description',
                        'sweep_number'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'volts')",
             'default': 'volts'})
    def __init__(self, **kwargs):
        name, data, unit, electrode, gain = popargs('name', 'data', 'unit', 'electrode', 'gain', kwargs)
        unit = ensure_unit(self, name, unit, 'volts', '2.1.0')
        super().__init__(name, data, unit, electrode, gain, **kwargs)


@register_class('SweepTable', CORE_NAMESPACE)
class SweepTable(DynamicTable):
    """
    A SweepTable allows to group PatchClampSeries together which stem from the same sweep.
    A sweep is a group of PatchClampSeries which have the same starting point in time.
    """

    __columns__ = (
            {'name': 'series', 'description': 'PatchClampSeries with the same sweep number',
             'required': True, 'index': True},
            {'name': 'sweep_number', 'description': 'Sweep number of the entries in that row', 'required': True}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this SweepTable', 'default': 'sweep_table'},
            {'name': 'description', 'type': str, 'doc': 'Description of this SweepTable',
             'default': "A sweep table groups different PatchClampSeries together."},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        call_docval_func(super().__init__, kwargs)

    @docval({'name': 'pcs', 'type': PatchClampSeries,
             'doc': 'PatchClampSeries to add to the table must have a valid sweep_number'})
    def add_entry(self, pcs):
        """
        Add the passed PatchClampSeries to the sweep table.
        """

        kwargs = {'sweep_number': pcs.sweep_number, 'series': [pcs]}

        # FIXME appending to an existing entry would be nicer
        # but this seems to be not possible
        self.add_row(**kwargs)

    def get_series(self, sweep_number):
        """
        Return a list of PatchClampSeries for the given sweep number.
        """

        ids = self.__get_row_ids(sweep_number)

        if len(ids) == 0:
            return None

        matches = []

        for x in ids:
            for y in self[(x, 'series')]:
                matches.append(y)

        return matches

    def __get_row_ids(self, sweep_number):
        """
        Return the row ids for the given sweep number.
        """

        return [index for index, elem in enumerate(self['sweep_number'].data) if elem == sweep_number]


def ensure_unit(self, name, current_unit, unit, nwb_version):
    """A helper to ensure correct unit used.

    Issues a warning with details if `current_unit` is to be ignored, and
    `unit` to be used instead.
    """
    if current_unit != unit:
        warnings.warn(
            "Unit '%s' for %s '%s' is ignored and will be set to '%s' "
            "as per NWB %s."
            % (current_unit, self.__class__.__name__, name, unit, nwb_version))
    return unit
