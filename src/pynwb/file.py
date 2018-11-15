from datetime import datetime
from dateutil.tz import tzlocal
from collections import Iterable
from warnings import warn
import copy as _copy

from .form.utils import docval, getargs, fmt_docval_args, call_docval_func, get_docval
from .form import Container

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, ProcessingModule
from .epoch import TimeIntervals
from .ecephys import ElectrodeGroup, Device
from .icephys import IntracellularElectrode, SweepTable, PatchClampSeries
from .ophys import ImagingPlane
from .ogen import OptogeneticStimulusSite
from .misc import Units
from .core import NWBContainer, NWBDataInterface, MultiContainerInterface, DynamicTable, DynamicTableRegion


def _not_parent(arg):
    return arg['name'] != 'parent'


@register_class('SpecFile', CORE_NAMESPACE)
class SpecFile(Container):
    # TODO: Implement this
    pass


@register_class('Subject', CORE_NAMESPACE)
class Subject(NWBContainer):

    __nwbfields__ = (
        'age',
        'description',
        'genotype',
        'sex',
        'species',
        'subject_id',
        'weight',
    )

    @docval({'name': 'age', 'type': str, 'doc': 'the age of the subject', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'a description of the subject', 'default': None},
            {'name': 'genotype', 'type': str, 'doc': 'the genotype of the subject', 'default': None},
            {'name': 'sex', 'type': str, 'doc': 'the sex of the subject', 'default': None},
            {'name': 'species', 'type': str, 'doc': 'the species of the subject', 'default': None},
            {'name': 'subject_id', 'type': str, 'doc': 'a unique identifier for the subject', 'default': None},
            {'name': 'weight', 'type': str, 'doc': 'the weight of the subject', 'default': None})
    def __init__(self, **kwargs):
        kwargs['name'] = 'subject'
        pargs, pkwargs = fmt_docval_args(super(Subject, self).__init__, kwargs)
        super(Subject, self).__init__(*pargs, **pkwargs)
        self.age = getargs('age', kwargs)
        self.description = getargs('description', kwargs)
        self.genotype = getargs('genotype', kwargs)
        self.sex = getargs('sex', kwargs)
        self.species = getargs('species', kwargs)
        self.subject_id = getargs('subject_id', kwargs)
        self.weight = getargs('weight', kwargs)


@register_class('NWBFile', CORE_NAMESPACE)
class NWBFile(MultiContainerInterface):
    """
    A representation of an NWB file.
    """

    __clsconf__ = [
        {
            'attr': 'acquisition',
            'add': '_add_acquisition_internal',
            'type': NWBDataInterface,
            'get': 'get_acquisition'
        },
        {
            'attr': 'analysis',
            'add': 'add_analysis',
            'type': NWBContainer,
            'get': 'get_analysis'
        },
        {
            'attr': 'stimulus',
            'add': '_add_stimulus_internal',
            'type': TimeSeries,
            'get': 'get_stimulus'
        },
        {
            'attr': 'stimulus_template',
            'add': '_add_stimulus_template_internal',
            'type': TimeSeries,
            'get': 'get_stimulus_template'
        },
        {
            'attr': 'modules',
            'add': 'add_processing_module',
            'type': ProcessingModule,
            'create': 'create_processing_module',
            'get': 'get_processing_module'
        },
        {
            'attr': 'devices',
            'add': 'add_device',
            'type': Device,
            'create': 'create_device',
            'get': 'get_device'
        },
        {
            'attr': 'electrode_groups',
            'add': 'add_electrode_group',
            'type': ElectrodeGroup,
            'create': 'create_electrode_group',
            'get': 'get_electrode_group'
        },
        {
            'attr': 'imaging_planes',
            'add': 'add_imaging_plane',
            'type': ImagingPlane,
            'create': 'create_imaging_plane',
            'get': 'get_imaging_plane'
        },
        {
            'attr': 'ic_electrodes',
            'add': 'add_ic_electrode',
            'type': IntracellularElectrode,
            'create': 'create_ic_electrode',
            'get': 'get_ic_electrode'
        },
        {
            'attr': 'ogen_sites',
            'add': 'add_ogen_site',
            'type': OptogeneticStimulusSite,
            'create': 'create_ogen_site',
            'get': 'get_ogen_site'
        },
        {
            'attr': 'time_intervals',
            'add': 'add_time_intervals',
            'type': TimeIntervals,
            'create': 'create_time_intervals',
            'get': 'get_time_intervals'
        },
    ]

    __nwbfields__ = ('timestamps_reference_time',
                     'file_create_date',
                     'experimenter',
                     'experiment_description',
                     'session_id',
                     'institution',
                     'keywords',
                     'notes',
                     'pharmacology',
                     'protocol',
                     'related_publications',
                     'slices',
                     'source_script',
                     'source_script_file_name',
                     'data_collection',
                     'surgery',
                     'virus',
                     'stimulus_notes',
                     'lab',
                     {'name': 'electrodes', 'child': True,  'required_name': 'electrodes'},
                     {'name': 'epochs', 'child': True, 'required_name': 'epochs'},
                     {'name': 'trials', 'child': True, 'required_name': 'trials'},
                     {'name': 'units', 'child': True, 'required_name': 'units'},
                     {'name': 'subject', 'child': True, 'required_name': 'subject'},
                     {'name': 'sweep_table', 'child': True, 'required_name': 'sweep_table'},
                     {'name': 'invalid_times', 'child': True, 'required_name': 'invalid_times'},
                     'epoch_tags',)

    @docval({'name': 'session_description', 'type': str,
             'doc': 'a description of the session where this data was generated'},
            {'name': 'identifier', 'type': str, 'doc': 'a unique text identifier for the file'},
            {'name': 'session_start_time', 'type': datetime, 'doc': 'the start date and time of the recording session'},
            {'name': 'file_create_date', 'type': ('array_data', datetime),
             'doc': 'the date and time the file was created and subsequent modifications made', 'default': None},
            {'name': 'timestamps_reference_time', 'type': datetime,
             'doc': 'date and time corresponding to time zero of all timestamps; defaults to value '
                    'of session_start_time', 'default': None},
            {'name': 'experimenter', 'type': str, 'doc': 'name of person who performed experiment', 'default': None},
            {'name': 'experiment_description', 'type': str,
             'doc': 'general description of the experiment', 'default': None},
            {'name': 'session_id', 'type': str, 'doc': 'lab-specific ID for the session', 'default': None},
            {'name': 'institution', 'type': str,
             'doc': 'institution(s) where experiment is performed', 'default': None},
            {'name': 'keywords', 'type': 'array_data', 'doc': 'Terms to search over', 'default': None},
            {'name': 'notes', 'type': str,
             'doc': 'Notes about the experiment.', 'default': None},
            {'name': 'pharmacology', 'type': str,
             'doc': 'Description of drugs used, including how and when they were administered. '
                    'Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.', 'default': None},
            {'name': 'protocol', 'type': str,
             'doc': 'Experimental protocol, if applicable. E.g., include IACUC protocol', 'default': None},
            {'name': 'related_publications', 'type': str,
             'doc': 'Publication information.'
             'PMID, DOI, URL, etc. If multiple, concatenate together and describe which is which. '
             'such as PMID, DOI, URL, etc', 'default': None},
            {'name': 'slices', 'type': str,
             'doc': 'Description of slices, including information about preparation '
             'thickness, orientation, temperature and bath solution', 'default': None},
            {'name': 'source_script', 'type': str,
             'doc': 'Script file used to create this NWB file.', 'default': None},
            {'name': 'source_script_file_name', 'type': str,
             'doc': 'Name of the source_script file', 'default': None},
            {'name': 'data_collection', 'type': str,
             'doc': 'Notes about data collection and analysis.', 'default': None},
            {'name': 'surgery', 'type': str,
             'doc': 'Narrative description about surgery/surgeries, including date(s) '
                    'and who performed surgery.', 'default': None},
            {'name': 'virus', 'type': str,
             'doc': 'Information about virus(es) used in experiments, including virus ID, '
                    'source, date made, injection location, volume, etc.', 'default': None},
            {'name': 'stimulus_notes', 'type': str,
             'doc': 'Notes about stimuli, such as how and where presented.', 'default': None},
            {'name': 'lab', 'type': str, 'doc': 'lab where experiment was performed', 'default': None},
            {'name': 'acquisition', 'type': (list, tuple),
             'doc': 'Raw TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus', 'type': (list, tuple),
             'doc': 'Stimulus TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus_template', 'type': (list, tuple),
             'doc': 'Stimulus template TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'epochs', 'type': TimeIntervals,
             'doc': 'Epoch objects belonging to this NWBFile', 'default': None},
            {'name': 'epoch_tags', 'type': (tuple, list, set),
             'doc': 'A sorted list of tags used across all epochs', 'default': set()},
            {'name': 'trials', 'type': TimeIntervals,
             'doc': 'A table containing trial data', 'default': None},
            {'name': 'invalid_times', 'type': TimeIntervals,
             'doc': 'A table containing times to be omitted from analysis', 'default': None},
            {'name': 'time_intervals', 'type': (list, tuple),
             'doc': 'any TimeIntervals tables storing time intervals', 'default': None},
            {'name': 'units', 'type': DynamicTable,
             'doc': 'A table containing unit metadata', 'default': None},
            {'name': 'modules', 'type': (list, tuple),
             'doc': 'ProcessingModule objects belonging to this NWBFile', 'default': None},
            {'name': 'electrodes', 'type': DynamicTable,
             'doc': 'the ElectrodeTable that belongs to this NWBFile', 'default': None},
            {'name': 'electrode_groups', 'type': Iterable,
             'doc': 'the ElectrodeGroups that belong to this NWBFile', 'default': None},
            {'name': 'ic_electrodes', 'type': (list, tuple),
             'doc': 'IntracellularElectrodes that belong to this NWBFile', 'default': None},
            {'name': 'sweep_table', 'type': SweepTable,
             'doc': 'the SweepTable that belong to this NWBFile', 'default': None},
            {'name': 'imaging_planes', 'type': (list, tuple),
             'doc': 'ImagingPlanes that belong to this NWBFile', 'default': None},
            {'name': 'ogen_sites', 'type': (list, tuple),
             'doc': 'OptogeneticStimulusSites that belong to this NWBFile', 'default': None},
            {'name': 'devices', 'type': (list, tuple),
             'doc': 'Device objects belonging to this NWBFile', 'default': None},
            {'name': 'subject', 'type': Subject,
             'doc': 'subject metadata', 'default': None})
    def __init__(self, **kwargs):
        pargs, pkwargs = fmt_docval_args(super(NWBFile, self).__init__, kwargs)
        pkwargs['name'] = 'root'
        super(NWBFile, self).__init__(*pargs, **pkwargs)
        self.__session_description = getargs('session_description', kwargs)
        self.__identifier = getargs('identifier', kwargs)

        self.__session_start_time = getargs('session_start_time', kwargs)
        if self.__session_start_time.tzinfo is None:
            self.__session_start_time = _add_missing_timezone(self.__session_start_time)

        self.__timestamps_reference_time = getargs('timestamps_reference_time', kwargs)
        if self.__timestamps_reference_time is None:
            self.__timestamps_reference_time = self.__session_start_time
        elif self.__timestamps_reference_time.tzinfo is None:
            raise ValueError("'timestamps_reference_time' must be a timezone-aware datetime object.")

        self.__file_create_date = getargs('file_create_date', kwargs)
        if self.__file_create_date is None:
            self.__file_create_date = datetime.now(tzlocal())
        if isinstance(self.__file_create_date, datetime):
            self.__file_create_date = [self.__file_create_date]
        self.__file_create_date = list(map(_add_missing_timezone, self.__file_create_date))

        self.acquisition = getargs('acquisition', kwargs)
        self.stimulus = getargs('stimulus', kwargs)
        self.stimulus_template = getargs('stimulus_template', kwargs)
        self.keywords = getargs('keywords', kwargs)

        self.modules = getargs('modules', kwargs)
        epochs = getargs('epochs', kwargs)
        if epochs is not None:
            if epochs.name != 'epochs':
                raise ValueError("NWBFile.epochs must be named 'epochs'")
            self.epochs = epochs
        self.epoch_tags = getargs('epoch_tags', kwargs)

        trials = getargs('trials', kwargs)
        if trials is not None:
            self.trials = trials
        invalid_times = getargs('invalid_times', kwargs)
        if invalid_times is not None:
            self.invalid_times = invalid_times
        units = getargs('units', kwargs)
        if units is not None:
            self.units = units

        self.electrodes = getargs('electrodes', kwargs)
        self.electrode_groups = getargs('electrode_groups', kwargs)
        self.devices = getargs('devices', kwargs)
        self.ic_electrodes = getargs('ic_electrodes', kwargs)
        self.imaging_planes = getargs('imaging_planes', kwargs)
        self.ogen_sites = getargs('ogen_sites', kwargs)
        self.time_intervals = getargs('time_intervals', kwargs)
        self.subject = getargs('subject', kwargs)
        self.sweep_table = getargs('sweep_table', kwargs)

        recommended = [
            'experimenter',
            'experiment_description',
            'session_id',
            'lab',
            'institution',
            'data_collection',
            'notes',
            'pharmacology',
            'protocol',
            'related_publications',
            'slices',
            'source_script',
            'source_script_file_name',
            'surgery',
            'virus',
            'stimulus_notes',
        ]
        for attr in recommended:
            setattr(self, attr, kwargs.get(attr, None))

        if getargs('source_script', kwargs) is None and getargs('source_script_file_name', kwargs) is not None:
            raise ValueError("'source_script' cannot be None when 'source_script_file_name' is set")

    def all_children(self):
        stack = [self]
        ret = list()
        while len(stack):
            n = stack.pop()
            ret.append(n)
            if hasattr(n, 'children'):
                for c in n.children:
                    stack.append(c)
        return ret

    @property
    def ec_electrode_groups(self):
        warn("replaced by NWBFile.electrode_groups", DeprecationWarning)
        return self.electrode_groups

    @property
    def ec_electrodes(self):
        warn("replaced by NWBFile.electrodes", DeprecationWarning)
        return self.electrodes

    @property
    def identifier(self):
        return self.__identifier

    @property
    def session_description(self):
        return self.__session_description

    @property
    def file_create_date(self):
        return self.__file_create_date

    @property
    def session_start_time(self):
        return self.__session_start_time

    @property
    def timestamps_reference_time(self):
        return self.__timestamps_reference_time

    def __check_epochs(self):
        if self.epochs is None:
            self.epochs = TimeIntervals('epochs', 'experimental epochs')

    @docval(*get_docval(TimeIntervals.add_column))
    def add_epoch_column(self, **kwargs):
        """
        Add a column to the electrode table.
        See :py:meth:`~pynwb.core.TimeIntervals.add_column` for more details
        """
        self.__check_epochs()
        self.epoch_tags.update(kwargs.pop('tags', list()))
        call_docval_func(self.epochs.add_column, kwargs)

    def add_epoch_metadata_column(self, *args, **kwargs):
        """
        This method is deprecated and will be removed in future versions. Please
        use :py:meth:`~pynwb.file.NWBFile.add_epoch_column` instead
        """
        raise DeprecationWarning("Please use NWBFile.add_epoch_column")

    @docval(*get_docval(TimeIntervals.add_interval),
            allow_extra=True)
    def add_epoch(self, **kwargs):
        """

        Creates a new Epoch object. Epochs are used to track intervals
        in an experiment, such as exposure to a certain type of stimuli
        (an interval where orientation gratings are shown, or of
        sparse noise) or a different paradigm (a rat exploring an
        enclosure versus sleeping between explorations)
        """
        self.__check_epochs()
        if kwargs['tags'] is not None:
            self.epoch_tags.update(kwargs['tags'])
        call_docval_func(self.epochs.add_interval, kwargs)

    def __check_electrodes(self):
        if self.electrodes is None:
            self.electrodes = ElectrodeTable()

    @docval(*get_docval(DynamicTable.add_column))
    def add_electrode_column(self, **kwargs):
        """
        Add a column to the electrode table.
        See :py:meth:`~pynwb.core.DynamicTable.add_column` for more details
        """
        self.__check_electrodes()
        call_docval_func(self.electrodes.add_column, kwargs)

    @docval({'name': 'x', 'type': float, 'doc': 'the x coordinate of the position'},
            {'name': 'y', 'type': float, 'doc': 'the y coordinate of the position'},
            {'name': 'z', 'type': float, 'doc': 'the z coordinate of the position'},
            {'name': 'imp', 'type': float, 'doc': 'the impedance of the electrode'},
            {'name': 'location', 'type': str, 'doc': 'the location of electrode within the subject e.g. brain region'},
            {'name': 'filtering', 'type': str, 'doc': 'description of hardware filtering'},
            {'name': 'group', 'type': ElectrodeGroup, 'doc': 'the ElectrodeGroup object to add to this NWBFile'},
            {'name': 'id', 'type': int, 'doc': 'a unique identifier for the electrode', 'default': None},
            allow_extra=True)
    def add_electrode(self, **kwargs):
        """
        Add a unit to the unit table.
        See :py:meth:`~pynwb.core.DynamicTable.add_row` for more details.

        Required fields are *x*, *y*, *z*, *imp*, *location*, *filtering*,
        *group* and any columns that have been added
        (through calls to `add_electrode_columns`).
        """
        self.__check_electrodes()
        d = _copy.copy(kwargs['data']) if kwargs.get('data') is not None else kwargs
        if d.get('group_name', None) is None:
            d['group_name'] = d['group'].name
        call_docval_func(self.electrodes.add_row, d)

    @docval({'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'electrodes'})
    def create_electrode_table_region(self, **kwargs):
        if self.electrodes is None:
            msg = "no electrodes available. add electrodes before creating a region"
            raise RuntimeError(msg)
        region = getargs('region', kwargs)
        for idx in region:
            if idx < 0 or idx >= len(self.electrodes):
                raise IndexError('The index ' + str(idx) +
                                 ' is out of range for the ElectrodeTable of length '
                                 + str(len(self.electrodes)))
        desc = getargs('description', kwargs)
        name = getargs('name', kwargs)
        return DynamicTableRegion(name, region, desc, self.electrodes)

    def __check_units(self):
        if self.units is None:
            self.units = Units(name='units', description='Autogenerated by NWBFile')

    @docval(*get_docval(Units.add_column))
    def add_unit_column(self, **kwargs):
        """
        Add a column to the unit table.
        See :py:meth:`~pynwb.core.DynamicTable.add_column` for more details
        """
        self.__check_units()
        call_docval_func(self.units.add_column, kwargs)

    @docval(*get_docval(Units.add_unit), allow_extra=True)
    def add_unit(self, **kwargs):
        """
        Add a unit to the unit table.
        See :py:meth:`~pynwb.core.DynamicTable.add_row` for more details.

        """
        self.__check_units()
        call_docval_func(self.units.add_unit, kwargs)

    def __check_trials(self):
        if self.trials is None:
            self.trials = TimeIntervals('trials', 'experimental trials')

    @docval(*get_docval(DynamicTable.add_column))
    def add_trial_column(self, **kwargs):
        """
        Add a column to the trial table.
        See :py:meth:`~pynwb.core.DynamicTable.add_column` for more details
        """
        self.__check_trials()
        call_docval_func(self.trials.add_column, kwargs)

    @docval(*get_docval(TimeIntervals.add_row), allow_extra=True)
    def add_trial(self, **kwargs):
        """
        Add a trial to the trial table.
        See :py:meth:`~pynwb.core.DynamicTable.add_row` for more details.

        Required fields are *start*, *end*, and any columns that have
        been added (through calls to `add_trial_columns`).
        """
        self.__check_trials()
        call_docval_func(self.trials.add_interval, kwargs)

    def __check_invalid_times(self):
        if self.invalid_times is None:
            self.invalid_times = TimeIntervals('invalid_times', 'time intervals to be removed from analysis')

    @docval(*get_docval(DynamicTable.add_column))
    def add_invalid_times_column(self, **kwargs):
        """
        Add a column to the trial table.
        See :py:meth:`~pynwb.core.DynamicTable.add_column` for more details
        """
        self.__check_invalid_times()
        call_docval_func(self.invalid_times.add_column, kwargs)

    def add_invalid_time_interval(self, **kwargs):
        """
        Add a trial to the trial table.
        See :py:meth:`~pynwb.core.DynamicTable.add_row` for more details.

        Required fields are *start_time*, *stop_time*, and any columns that have
        been added (through calls to `add_invalid_times_columns`).
        """
        self.__check_invalid_times()
        call_docval_func(self.invalid_times.add_interval, kwargs)

    @docval({'name': 'electrode_table', 'type': DynamicTable, 'doc': 'the ElectrodeTable for this file'})
    def set_electrode_table(self, **kwargs):
        """
        Set the electrode table of this NWBFile to an existing ElectrodeTable
        """
        if self.electrodes is not None:
            msg = 'ElectrodeTable already exists, cannot overwrite'
            raise ValueError(msg)
        electrode_table = getargs('electrode_table', kwargs)
        self.electrodes = electrode_table

    def _check_sweep_table(self):
        """
        Create a SweepTable if not yet done.
        """
        if self.sweep_table is None:
            self.sweep_table = SweepTable(name='sweep_table')

    def _update_sweep_table(self, nwbdata):
        """
        Add all PatchClampSeries with a valid sweep number to the sweep_table
        """

        if isinstance(nwbdata, PatchClampSeries):
            if nwbdata.sweep_number is not None:
                self._check_sweep_table()
                self.sweep_table.add_entry(nwbdata)

    @docval({'name': 'nwbdata', 'type': NWBDataInterface})
    def add_acquisition(self, nwbdata):
        self._add_acquisition_internal(nwbdata)
        self._update_sweep_table(nwbdata)

    @docval({'name': 'timeseries', 'type': TimeSeries})
    def add_stimulus(self, timeseries):
        self._add_stimulus_internal(timeseries)
        self._update_sweep_table(timeseries)

    @docval({'name': 'timeseries', 'type': TimeSeries})
    def add_stimulus_template(self, timeseries):
        self._add_stimulus_template_internal(timeseries)
        self._update_sweep_table(timeseries)


def _add_missing_timezone(date):
    """
    Add local timezone information on a datetime object if it is missing.
    """
    if not isinstance(date, datetime):
        raise ValueError("require datetime object")
    if date.tzinfo is None:
        warn("Date is missing timezone information. Updating to local timezone.")
        return date.replace(tzinfo=tzlocal())
    return date


def _tablefunc(table_name, description, columns):
    t = DynamicTable(table_name, description)
    for c in columns:
        if isinstance(c, tuple):
            t.add_column(c[0], c[1])
        elif isinstance(c, str):
            t.add_column(c)
        else:
            raise ValueError("Elements of 'columns' must be str or tuple")
    return t


def ElectrodeTable(name='electrodes',
                   description='metadata about extracellular electrodes'):
    return _tablefunc(name, description,
                      [('x', 'the x coordinate of the channel location'),
                       ('y', 'the y coordinate of the channel location'),
                       ('z', 'the z coordinate of the channel location'),
                       ('imp', 'the impedance of the channel'),
                       ('location', 'the location of channel within the subject e.g. brain region'),
                       ('filtering', 'description of hardware filtering'),
                       ('group', 'a reference to the ElectrodeGroup this electrode is a part of'),
                       ('group_name', 'the name of the ElectrodeGroup this electrode is a part of')]
                      )


def TrialTable(name='trials',
               description='metadata about experimental trials'):
    return _tablefunc(name, description, ['start', 'end'])


def InvalidTimesTable(name='invalid_times', description='time intervals to be removed from analysis'):
    return _tablefunc(name, description, ['start_time', 'stop_time'])
