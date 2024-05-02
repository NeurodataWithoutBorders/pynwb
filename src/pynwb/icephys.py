import warnings
from copy import copy

import numpy as np

from hdmf.common import DynamicTable, AlignedDynamicTable
from hdmf.utils import docval, popargs, popargs_to_dict, get_docval, getargs

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, TimeSeriesReferenceVectorData
from .core import NWBContainer
from .device import Device


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


@register_class('IntracellularElectrode', CORE_NAMESPACE)
class IntracellularElectrode(NWBContainer):
    """Describes an intracellular electrode and associated metadata."""

    __nwbfields__ = ('cell_id',
                     'slice',
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
             'doc': 'Recording description, description of electrode (e.g.,  whole-cell, sharp, etc).'},
            {'name': 'slice', 'type': str, 'doc': 'Information about slice used for recording.', 'default': None},
            {'name': 'seal', 'type': str, 'doc': 'Information about seal used for recording.', 'default': None},
            {'name': 'location', 'type': str,
             'doc': 'Area, layer, comments on estimation, stereotaxis coordinates (if in vivo, etc).', 'default': None},
            {'name': 'resistance', 'type': str, 'doc': 'Electrode resistance, unit - Ohm.', 'default': None},
            {'name': 'filtering', 'type': str, 'doc': 'Electrode specific filtering.', 'default': None},
            {'name': 'initial_access_resistance', 'type': str, 'doc': 'Initial access resistance.', 'default': None},
            {'name': 'cell_id', 'type': str, 'doc': 'Unique ID of cell.', 'default': None}
            )
    def __init__(self, **kwargs):
        keys_to_set = (
            'slice',
            'seal',
            'description',
            'location',
            'resistance',
            'filtering',
            'initial_access_resistance',
            'device',
            'cell_id'
        )
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)


@register_class('PatchClampSeries', CORE_NAMESPACE)
class PatchClampSeries(TimeSeries):
    '''
    Stores stimulus or response current or voltage. Superclass definition for patch-clamp data
    (this class should not be instantiated directly).
    '''

    __nwbfields__ = (
        'electrode',
        'gain',
        'stimulus_description',
        'sweep_number',
    )

    @docval(
        *get_docval(TimeSeries.__init__, 'name'),  # required
        {
            "name": "data",
            "type": ("array_data", "data", TimeSeries),
            "doc": "The data values. The first dimension must be time.",
            "shape": (None,),
        },   # required
        {
            'name': 'unit',
            'type': str,
            'doc': 'The base unit of measurement (should be SI unit)',
        },  # required
        {
            'name': 'electrode',
            'type': IntracellularElectrode,
            'doc': 'IntracellularElectrode group that describes the electrode that was '
                   'used to apply or record this data.',
        },    # required
        {
            'name': 'gain',
            'type': float,
            'doc': 'Units: Volt/Amp (v-clamp) or Volt/Volt (c-clamp)',
        },  # required
        {
            'name': 'stimulus_description',
            'type': str,
            'doc': 'the stimulus name/protocol',
            'default': "N/A",
        },
        *get_docval(
            TimeSeries.__init__,
            'resolution',
            'conversion',
            'timestamps',
            'starting_time',
            'rate',
            'comments',
            'description',
            'control',
            'control_description',
            'offset',
        ),
        {
            'name': 'sweep_number', 'type': (int, 'uint32', 'uint64'),
            'doc': 'Sweep number, allows for grouping different PatchClampSeries '
                   'together via the sweep_table',
            'default': None,
        }
    )
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
            {'name': 'gain', 'type': float, 'doc': 'Units - Volt/Volt'},
            *get_docval(PatchClampSeries.__init__, 'stimulus_description'),
            {'name': 'bias_current', 'type': float, 'doc': 'Unit - Amp', 'default': None},
            {'name': 'bridge_balance', 'type': float, 'doc': 'Unit - Ohm', 'default': None},
            {'name': 'capacitance_compensation', 'type': float, 'doc': 'Unit - Farad', 'default': None},
            *get_docval(PatchClampSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'sweep_number', 'offset'),
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
            {'name': 'gain', 'type': float, 'doc': 'Units: Volt/Volt'},  # required
            {'name': 'stimulus_description', 'type': str,
             'doc': ('The stimulus name/protocol. Setting this to a value other than "N/A" is deprecated as of '
                     'NWB 2.3.0.'),
             'default': 'N/A'},
            *get_docval(CurrentClampSeries.__init__, 'resolution', 'conversion', 'timestamps',
                        'starting_time', 'rate', 'comments', 'description', 'control', 'control_description',
                        'sweep_number', 'offset'),
            {'name': 'unit', 'type': str, 'doc': "The base unit of measurement (must be 'volts')",
             'default': 'volts'})
    def __init__(self, **kwargs):
        name, data, electrode, gain = popargs('name', 'data', 'electrode', 'gain', kwargs)
        bias_current, bridge_balance, capacitance_compensation = (0.0, 0.0, 0.0)
        stimulus_description = popargs('stimulus_description', kwargs)
        stimulus_description = self._ensure_stimulus_description(name, stimulus_description, 'N/A', '2.3.0')
        kwargs['stimulus_description'] = stimulus_description
        super().__init__(name, data, electrode, gain, bias_current, bridge_balance, capacitance_compensation,
                         **kwargs)

    def _ensure_stimulus_description(self, name, current_stim_desc, stim_desc, nwb_version):
        """A helper to ensure correct stimulus_description used.

        Issues a warning with details if `current_stim_desc` is to be ignored, and
        `stim_desc` to be used instead.
        """
        if current_stim_desc != stim_desc:
            warnings.warn(
                "Stimulus description '%s' for %s '%s' is ignored and will be set to '%s' "
                "as per NWB %s."
                % (current_stim_desc, self.__class__.__name__, name, stim_desc, nwb_version))
        return stim_desc


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
                        'sweep_number', 'offset'),
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
            {'name': 'gain', 'type': float, 'doc': 'Units - Volt/Amp'},  # required
            *get_docval(PatchClampSeries.__init__, 'stimulus_description'),
            {'name': 'capacitance_fast', 'type': float, 'doc': 'Unit - Farad', 'default': None},
            {'name': 'capacitance_slow', 'type': float, 'doc': 'Unit - Farad', 'default': None},
            {'name': 'resistance_comp_bandwidth', 'type': float, 'doc': 'Unit - Hz', 'default': None},
            {'name': 'resistance_comp_correction', 'type': float, 'doc': 'Unit - percent', 'default': None},
            {'name': 'resistance_comp_prediction', 'type': float, 'doc': 'Unit - percent', 'default': None},
            {'name': 'whole_cell_capacitance_comp', 'type': float, 'doc': 'Unit - Farad', 'default': None},
            {'name': 'whole_cell_series_resistance_comp', 'type': float, 'doc': 'Unit - Ohm', 'default': None},
            *get_docval(PatchClampSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'sweep_number', 'offset'),
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
                        'sweep_number', 'offset'),
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
        warnings.warn("Use of SweepTable is deprecated. Use the IntracellularRecordingsTable "
                      "instead. See also the  NWBFile.add_intracellular_recordings function.",
                      DeprecationWarning)
        super().__init__(**kwargs)

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


@register_class('IntracellularElectrodesTable', CORE_NAMESPACE)
class IntracellularElectrodesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata'
    """
    __columns__ = (
        {'name': 'electrode',
         'description': 'Column for storing the reference to the intracellular electrode',
         'required': True,
         'index': False,
         'table': False},
    )

    @docval(*get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        # Define defaultb name and description settings
        kwargs['name'] = 'electrodes'
        kwargs['description'] = ('Table for storing intracellular electrode related metadata')
        # Initialize the DynamicTable
        super().__init__(**kwargs)


@register_class('IntracellularStimuliTable', CORE_NAMESPACE)
class IntracellularStimuliTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata'
    """
    __columns__ = (
        {'name': 'stimulus',
         'description': 'Column storing the reference to the recorded stimulus for the recording (rows)',
         'required': True,
         'index': False,
         'table': False,
         'class': TimeSeriesReferenceVectorData},
        {'name': 'stimulus_template',
         'description': 'Column storing the reference to the stimulus template for the recording (rows)',
         'required': False,
         'index': False,
         'table': False,
         'class': TimeSeriesReferenceVectorData},
    )

    @docval(*get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        # Define defaultb name and description settings
        kwargs['name'] = 'stimuli'
        kwargs['description'] = ('Table for storing intracellular stimulus related metadata')
        # Initialize the DynamicTable
        super().__init__(**kwargs)


@register_class('IntracellularResponsesTable', CORE_NAMESPACE)
class IntracellularResponsesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata'
    """
    __columns__ = (
        {'name': 'response',
         'description': 'Column storing the reference to the recorded response for the recording (rows)',
         'required': True,
         'index': False,
         'table': False,
         'class': TimeSeriesReferenceVectorData},
    )

    @docval(*get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        # Define defaultb name and description settings
        kwargs['name'] = 'responses'
        kwargs['description'] = ('Table for storing intracellular response related metadata')
        # Initialize the DynamicTable
        super().__init__(**kwargs)


@register_class('IntracellularRecordingsTable', CORE_NAMESPACE)
class IntracellularRecordingsTable(AlignedDynamicTable):
    """
    A table to group together a stimulus and response from a single electrode and
    a single simultaneous_recording. Each row in the table represents a single recording consisting
    typically of a stimulus and a corresponding response.
    """
    @docval(*get_docval(AlignedDynamicTable.__init__, 'id', 'columns', 'colnames', 'category_tables', 'categories'))
    def __init__(self, **kwargs):
        kwargs['name'] = 'intracellular_recordings'
        kwargs['description'] = ('A table to group together a stimulus and response from a single electrode '
                                 'and a single simultaneous recording and for storing metadata about the '
                                 'intracellular recording.')
        in_category_tables = getargs('category_tables', kwargs)
        if in_category_tables is None or len(in_category_tables) == 0:
            kwargs['category_tables'] = [IntracellularElectrodesTable(),
                                         IntracellularStimuliTable(),
                                         IntracellularResponsesTable()]
            kwargs['categories'] = None
        else:
            # Check if our required data tables are supplied, otherwise add them to the list
            required_dynamic_table_given = [-1 for i in range(3)]  # The first three are our required tables
            for i, tab in enumerate(in_category_tables):
                if isinstance(tab, IntracellularElectrodesTable):
                    required_dynamic_table_given[0] = i
                elif isinstance(tab, IntracellularStimuliTable):
                    required_dynamic_table_given[1] = i
                elif isinstance(tab, IntracellularResponsesTable):
                    required_dynamic_table_given[2] = i
            # Check if the supplied tables contain data but not all required tables have been supplied
            required_dynamic_table_missing = np.any(np.array(required_dynamic_table_given[0:3]) < 0)
            if len(in_category_tables[0]) != 0 and required_dynamic_table_missing:
                raise ValueError("IntracellularElectrodeTable, IntracellularStimuliTable, and "
                                 "IntracellularResponsesTable are required when adding custom, non-empty "
                                 "tables to IntracellularRecordingsTable as the missing data for the required "
                                 "tables cannot be determined automatically")
            # Compile the complete list of tables
            dynamic_table_arg = copy(in_category_tables)
            categories_arg = [] if getargs('categories', kwargs) is None else copy(getargs('categories', kwargs))
            if required_dynamic_table_missing:
                if required_dynamic_table_given[2] < 0:
                    dynamic_table_arg.append(IntracellularResponsesTable)
                    if dynamic_table_arg[-1].name not in categories_arg:
                        categories_arg.insert(0, dynamic_table_arg[-1].name)
                if required_dynamic_table_given[1] < 0:
                    dynamic_table_arg.append(IntracellularStimuliTable())
                    if dynamic_table_arg[-1].name not in categories_arg:
                        categories_arg.insert(0, dynamic_table_arg[-1].name)
                if required_dynamic_table_given[0] < 0:
                    dynamic_table_arg.append(IntracellularElectrodesTable())
                    if dynamic_table_arg[-1].name not in categories_arg:
                        categories_arg.insert(0, dynamic_table_arg[-1].name)
            kwargs['category_tables'] = dynamic_table_arg
            kwargs['categories'] = categories_arg

        super().__init__(**kwargs)

    @docval(
        {
            "name": "electrode",
            "type": IntracellularElectrode,
            "doc": "The intracellular electrode used",
            "default": None,
        },
        {'name': 'stimulus_start_index', 'type': int, 'doc': 'Start index of the stimulus', 'default': None},
        {'name': 'stimulus_index_count', 'type': int, 'doc': 'Stop index of the stimulus', 'default': None},
        {'name': 'stimulus', 'type': TimeSeries,
         'doc': 'The TimeSeries (usually a PatchClampSeries) with the stimulus',
         'default': None},
        {'name': 'stimulus_template_start_index', 'type': int, 'doc': 'Start index of the stimulus template',
         'default': None},
        {'name': 'stimulus_template_index_count', 'type': int, 'doc': 'Stop index of the stimulus template',
         'default': None},
        {'name': 'stimulus_template', 'type': TimeSeries,
         'doc': 'The TimeSeries (usually a PatchClampSeries) with the stimulus template waveforms',
         'default': None},
        {'name': 'response_start_index', 'type': int, 'doc': 'Start index of the response', 'default': None},
        {'name': 'response_index_count', 'type': int, 'doc': 'Stop index of the response', 'default': None},
        {'name': 'response', 'type': TimeSeries,
         'doc': 'The TimeSeries (usually a PatchClampSeries) with the response',
         'default': None},
        {'name': 'electrode_metadata', 'type': dict,
         'doc': 'Additional electrode metadata to be stored in the electrodes table', 'default': None},
        {'name': 'stimulus_metadata', 'type': dict,
         'doc': 'Additional stimulus metadata to be stored in the stimuli table', 'default': None},
        {'name': 'response_metadata', 'type': dict,
         'doc': 'Additional resposnse metadata to be stored in the responses table', 'default': None},
        returns='Integer index of the row that was added to this table',
        rtype=int,
        allow_extra=True,
    )
    def add_recording(self, **kwargs):
        """
        Add a single recording to the IntracellularRecordingsTable table.

        Typically, both stimulus and response are expected. However, in some cases only a stimulus
        or a response may be recodred as part of a recording. In this case, None may be given
        for either stimulus or response, but not both. Internally, this results in both stimulus
        and response pointing to the same TimeSeries, while the start_index and index_count for
        the invalid series will both be set to -1.
        """
        # Get the input data
        stimulus_start_index, stimulus_index_count, stimulus = popargs('stimulus_start_index',
                                                                       'stimulus_index_count',
                                                                       'stimulus',
                                                                       kwargs)
        response_start_index, response_index_count, response = popargs('response_start_index',
                                                                       'response_index_count',
                                                                       'response',
                                                                       kwargs)
        electrode = popargs('electrode', kwargs)
        stimulus_template_start_index, stimulus_template_index_count, stimulus_template = popargs(
            'stimulus_template_start_index',
            'stimulus_template_index_count',
            'stimulus_template',
            kwargs)

        # if electrode is not provided, take from stimulus or response object
        if electrode is None:
            if stimulus:
                electrode = stimulus.electrode
            elif response:
                electrode = response.electrode

        # Confirm that we have at least a valid stimulus or response
        if stimulus is None and response is None:
            raise ValueError("stimulus and response cannot both be None.")

        # Compute the start and stop index if necessary
        stimulus_start_index, stimulus_index_count = self.__compute_index(stimulus_start_index,
                                                                          stimulus_index_count,
                                                                          stimulus, 'stimulus')
        response_start_index, response_index_count = self.__compute_index(response_start_index,
                                                                          response_index_count,
                                                                          response, 'response')
        stimulus_template_start_index, stimulus_template_index_count = self.__compute_index(
            stimulus_template_start_index,
            stimulus_template_index_count,
            stimulus_template, 'stimulus_template')

        # if stimulus template is already a column in the stimuli table, but stimulus_template was None
        if 'stimulus_template' in self.category_tables['stimuli'].colnames and stimulus_template is None:
            stimulus_template = stimulus if stimulus is not None else response  # set to stimulus if it was provided

        # If either stimulus or response are None, then set them to the same TimeSeries to keep the I/O happy
        response = response if response is not None else stimulus
        stimulus_provided_is_not_none = stimulus is not None  # Store if stimulus is None for error checks later
        stimulus = stimulus if stimulus_provided_is_not_none else response

        # Make sure the types are compatible.
        if ((response.neurodata_type.startswith("CurrentClamp") and
                stimulus.neurodata_type.startswith("VoltageClamp")) or
                (response.neurodata_type.startswith("VoltageClamp") and
                 stimulus.neurodata_type.startswith("CurrentClamp"))):
            raise ValueError("Incompatible types given for 'stimulus' and 'response' parameters. "
                             "'stimulus' is of type %s and 'response' is of type %s." %
                             (stimulus.neurodata_type, response.neurodata_type))
        if response.neurodata_type == 'IZeroClampSeries':
            if stimulus_provided_is_not_none:
                raise ValueError("stimulus should usually be None for IZeroClampSeries response")
        if isinstance(response, PatchClampSeries) and isinstance(stimulus, PatchClampSeries):
            # # We could also check sweep_number, but since it is mostly relevant to the deprecated SweepTable
            # # we don't really need to enforce it here
            # if response.sweep_number != stimulus.sweep_number:
            #     warnings.warn("sweep_number are usually expected to be the same for PatchClampSeries type "
            #                   "stimulus and response pairs in an intracellular recording.")
            if response.electrode != stimulus.electrode:
                raise ValueError(
                    "electrodes are usually expected to be the same for PatchClampSeries type stimulus and response "
                    "pairs in an intracellular recording."
                )

        # Compile the electrodes table data
        electrodes = copy(popargs('electrode_metadata', kwargs))
        if electrodes is None:
            electrodes = {}
        electrodes['electrode'] = electrode

        # Compile the stimuli table data
        stimuli = copy(popargs('stimulus_metadata', kwargs))
        if stimuli is None:
            stimuli = {}
        stimuli['stimulus'] = TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(
            stimulus_start_index, stimulus_index_count, stimulus)
        if stimulus_template is not None:
            stimuli['stimulus_template'] = TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(
                stimulus_template_start_index, stimulus_template_index_count, stimulus_template)

        # Compile the responses table data
        responses = copy(popargs('response_metadata', kwargs))
        if responses is None:
            responses = {}
        responses['response'] = TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(
            response_start_index, response_index_count, response)

        _ = super().add_row(enforce_unique_id=True,
                            electrodes=electrodes,
                            responses=responses,
                            stimuli=stimuli,
                            **kwargs)
        return len(self) - 1

    @staticmethod
    def __compute_index(start_index, index_count, time_series, name):
        """
        Internal helper function to compute the start_index and index_count
        to use for the stimulus and response column

        :param start_index: The start_index provided by the user
        :param index_count: The index count provided by the user
        :param time_series: The timeseries object to reference. May be None.
        :param name: Name of the table. Used only to enhance error reporting

        :raises IndexError: If index_count cannot be determined or start_index+index_count
            are outside of the range of the timeseries.

        :returns: A tuple of integers with the start_index and index_count to use.
        """
        # If times_series is not valid then return -1, -1 to indicate invalid times
        if time_series is None:
            return -1, -1
        # Since time_series is valid, negative or None start_index means the user did not specify a start_index
        # so we now need to set it to 0
        if start_index is None or start_index < 0:
            start_index = 0
        # If index_count has not been set yet (i.e., it is -1 or None) then attempt to set it to the
        # full range of the timeseries starting from start_index
        num_samples = time_series.num_samples
        if index_count is None or index_count < 0:
            index_count = (num_samples - start_index) if num_samples is not None else None
        # Check that the start_index and index_count are valid and raise IndexError if they are invalid
        if index_count is None:
            raise IndexError("Invalid %s_index_count cannot be determined from %s data." % (name, name))
        if num_samples is not None:
            if start_index >= num_samples:
                raise IndexError("%s_start_index out of range" % name)
            if (start_index + index_count) > num_samples:
                raise IndexError("%s_start_index + %s_index_count out of range" % (name, name))
        # Return the values
        return start_index, index_count

    @docval(*get_docval(AlignedDynamicTable.to_dataframe, 'ignore_category_ids'),
            {'name': 'electrode_refs_as_objectids', 'type': bool,
             'doc': 'replace object references in the electrode column with object_ids',
             'default': False},
            {'name': 'stimulus_refs_as_objectids', 'type': bool,
             'doc': 'replace object references in the stimulus column with object_ids',
             'default': False},
            {'name': 'response_refs_as_objectids', 'type': bool,
             'doc': 'replace object references in the response column with object_ids',
             'default': False}
            )
    def to_dataframe(self, **kwargs):
        """Convert the collection of tables to a single pandas DataFrame"""
        res = super().to_dataframe(ignore_category_ids=getargs('ignore_category_ids', kwargs))
        if getargs('electrode_refs_as_objectids', kwargs):
            res[('electrodes', 'electrode')] = [e.object_id for e in res[('electrodes', 'electrode')]]
        if getargs('stimulus_refs_as_objectids', kwargs):
            res[('stimuli', 'stimulus')] = \
                [e if e[2] is None
                 else TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(e[0], e[1],  e[2].object_id)
                 for e in res[('stimuli', 'stimulus')]]
        if getargs('response_refs_as_objectids', kwargs):
            res[('responses', 'response')] = \
                [e if e[2] is None else
                 TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(e[0], e[1],  e[2].object_id)
                 for e in res[('responses', 'response')]]
        return res


@register_class('SimultaneousRecordingsTable', CORE_NAMESPACE)
class SimultaneousRecordingsTable(DynamicTable):
    """
    A table for grouping different intracellular recordings from the
    IntracellularRecordingsTable table together that were recorded simultaneously
    from different electrodes.
    """

    __columns__ = (
        {'name': 'recordings',
         'description': 'Column with references to one or more rows in the IntracellularRecordingsTable table',
         'required': True,
         'index': True,
         'table': True},
    )

    @docval({'name': 'intracellular_recordings_table',
             'type': IntracellularRecordingsTable,
             'doc': 'the IntracellularRecordingsTable table that the recordings column indexes. May be None when '
                    'reading the Container from file as the table attribute is already populated in this case '
                    'but otherwise this is required.',
             'default': None},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        intracellular_recordings_table = popargs('intracellular_recordings_table', kwargs)
        # Define default name and description settings
        kwargs['name'] = 'simultaneous_recordings'
        kwargs['description'] = ('A table for grouping different intracellular recordings from the'
                                 'IntracellularRecordingsTable table together that were recorded simultaneously '
                                 'from different electrodes.')
        # Initialize the DynamicTable
        super().__init__(**kwargs)
        if self['recordings'].target.table is None:
            if intracellular_recordings_table is not None:
                self['recordings'].target.table = intracellular_recordings_table
            else:
                raise ValueError("intracellular_recordings constructor argument required")

    @docval({'name': 'recordings',
             'type': 'array_data',
             'doc': 'the indices of the recordings belonging to this simultaneous recording'},
            returns='Integer index of the row that was added to this table',
            rtype=int,
            allow_extra=True)
    def add_simultaneous_recording(self, **kwargs):
        """
        Add a single simultaneous recording (i.e., one sweep, or one row) consisting of one or more
        recordings and associated custom simultaneous recording metadata to the table.
        """
        _ = super().add_row(enforce_unique_id=True, **kwargs)
        return len(self.id) - 1


@register_class('SequentialRecordingsTable', CORE_NAMESPACE)
class SequentialRecordingsTable(DynamicTable):
    """
    A table for grouping different intracellular recording simultaneous_recordings from the
    SimultaneousRecordingsTable table together. This is typically used to group together simultaneous_recordings
    where the a sequence of stimuli of the same type with varying parameters
    have been presented in a sequence.
    """

    __columns__ = (
        {'name': 'simultaneous_recordings',
         'description': 'Column with references to one or more rows in the SimultaneousRecordingsTable table',
         'required': True,
         'index': True,
         'table': True},
        {'name': 'stimulus_type',
         'description': 'Column storing the type of stimulus used for the sequential recording',
         'required': True,
         'index': False,
         'table': False}
    )

    @docval({'name': 'simultaneous_recordings_table',
             'type': SimultaneousRecordingsTable,
             'doc': 'the SimultaneousRecordingsTable table that the simultaneous_recordings '
                    'column indexes. May be None when reading the Container from file as the '
                    'table attribute is already populated in this case but otherwise this is required.',
             'default': None},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        simultaneous_recordings_table = popargs('simultaneous_recordings_table', kwargs)
        # Define defaultb name and description settings
        kwargs['name'] = 'sequential_recordings'
        kwargs['description'] = ('A table for grouping different intracellular recording simultaneous_recordings '
                                 'from the SimultaneousRecordingsTable table together. This is typically used to '
                                 'group together simultaneous_recordings where the a sequence of stimuli of the '
                                 'same type with varying parameters have been presented in a sequence.')
        # Initialize the DynamicTable
        super().__init__(**kwargs)
        if self['simultaneous_recordings'].target.table is None:
            if simultaneous_recordings_table is not None:
                self['simultaneous_recordings'].target.table = simultaneous_recordings_table
            else:
                raise ValueError('simultaneous_recordings_table constructor argument required')

    @docval({'name': 'stimulus_type',
             'type': str,
             'doc': 'the type of stimulus used for the sequential recording'},
            {'name': 'simultaneous_recordings',
             'type': 'array_data',
             'doc': 'the indices of the simultaneous_recordings belonging to this sequential recording'},
            returns='Integer index of the row that was added to this table',
            rtype=int,
            allow_extra=True)
    def add_sequential_recording(self, **kwargs):
        """
        Add a sequential recording (i.e., one row) consisting of one or more simultaneous recordings
        and associated custom sequential recording metadata to the table.
        """
        _ = super().add_row(enforce_unique_id=True, **kwargs)
        return len(self.id) - 1


@register_class('RepetitionsTable', CORE_NAMESPACE)
class RepetitionsTable(DynamicTable):
    """
    A table for grouping different intracellular recording sequential recordings together.
    With each SweepSequence typically representing a particular type of stimulus, the
    RepetitionsTable table is typically used to group sets of stimuli applied in sequence.
    """

    __columns__ = (
        {'name': 'sequential_recordings',
         'description': 'Column with references to one or more rows in the SequentialRecordingsTable table',
         'required': True,
         'index': True,
         'table': True},
    )

    @docval({'name': 'sequential_recordings_table',
             'type': SequentialRecordingsTable,
             'doc': 'the SequentialRecordingsTable table that the sequential_recordings column indexes. May '
                    'be None when reading the Container from file as the table attribute is already populated '
                    'in this case but otherwise this is required.',
             'default': None},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        sequential_recordings_table = popargs('sequential_recordings_table', kwargs)
        # Define default name and description settings
        kwargs['name'] = 'repetitions'
        kwargs['description'] = ('A table for grouping different intracellular recording sequential recordings '
                                 'together. With each SimultaneousRecording typically representing a particular type '
                                 'of stimulus, the RepetitionsTable table is typically used to group sets '
                                 'of stimuli applied in sequence.')
        # Initialize the DynamicTable
        super().__init__(**kwargs)
        if self['sequential_recordings'].target.table is None:
            if sequential_recordings_table is not None:
                self['sequential_recordings'].target.table = sequential_recordings_table
            else:
                raise ValueError('sequential_recordings_table constructor argument required')

    @docval({'name': 'sequential_recordings',
             'type': 'array_data',
             'doc': 'the indices of the sequential recordings belonging to this repetition',
             'default': None},
            returns='Integer index of the row that was added to this table',
            rtype=int,
            allow_extra=True)
    def add_repetition(self, **kwargs):
        """
        Add a repetition (i.e., one row) consisting of one or more sequential recordings
        and associated custom repetition metadata to the table.
        """
        _ = super().add_row(enforce_unique_id=True, **kwargs)
        return len(self.id) - 1


@register_class('ExperimentalConditionsTable', CORE_NAMESPACE)
class ExperimentalConditionsTable(DynamicTable):
    """
    A table for grouping different intracellular recording repetitions together that
    belong to the same experimental conditions.
    """

    __columns__ = (
        {'name': 'repetitions',
         'description': 'Column with references to one or more rows in the RepetitionsTable table',
         'required': True,
         'index': True,
         'table': True},
    )

    @docval({'name': 'repetitions_table',
             'type': RepetitionsTable,
             'doc': 'the RepetitionsTable table that the repetitions column indexes',
             'default': None},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        repetitions_table = popargs('repetitions_table', kwargs)
        # Define default name and description settings
        kwargs['name'] = 'experimental_conditions'
        kwargs['description'] = ('A table for grouping different intracellular recording repetitions together that '
                                 'belong to the same experimental conditions.')
        # Initialize the DynamicTable
        super().__init__(**kwargs)
        if self['repetitions'].target.table is None:
            if repetitions_table is not None:
                self['repetitions'].target.table = repetitions_table
            else:
                raise ValueError('repetitions_table constructor argument required')

    @docval({'name': 'repetitions',
             'type': 'array_data',
             'doc': 'the indices of the repetitions belonging to this condition',
             'default': None},
            returns='Integer index of the row that was added to this table',
            rtype=int,
            allow_extra=True)
    def add_experimental_condition(self, **kwargs):
        """
        Add a condition (i.e., one row) consisting of one or more repetitions of sequential recordings
        and associated custom experimental_conditions metadata to the table.
        """
        _ = super().add_row(enforce_unique_id=True, **kwargs)
        return len(self.id) - 1
