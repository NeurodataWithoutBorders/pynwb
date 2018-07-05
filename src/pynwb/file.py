from datetime import datetime
from dateutil.parser import parse as parse_date
from collections import Iterable

from .form.utils import docval, getargs, fmt_docval_args, call_docval_func, get_docval
from .form import Container

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, ProcessingModule
from .epoch import Epochs
from .ecephys import ElectrodeTable, ElectrodeTableRegion, ElectrodeGroup, Device
from .icephys import IntracellularElectrode
from .ophys import ImagingPlane
from .ogen import OptogeneticStimulusSite
from .core import NWBContainer, NWBData, NWBDataInterface, MultiContainerInterface, DynamicTable

from h5py import RegionReference


def _not_parent(arg):
    return arg['name'] != 'parent'


# @register_class('Image', CORE_NAMESPACE)
class Image(NWBData):
    # TODO: Implement this
    pass


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
            {'name': 'weight', 'type': str, 'doc': 'the weight of the subject', 'default': None},
            {'name': 'source', 'type': str, 'doc': 'the source of this information', 'default': None})
    def __init__(self, **kwargs):
        kwargs['name'] = 'subject'
        kwargs['source'] = getargs('source', kwargs)
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
            'add': 'add_acquisition',
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
            'add': 'add_stimulus',
            'type': TimeSeries,
            'get': 'get_stimulus'
        },
        {
            'attr': 'stimulus_template',
            'add': 'add_stimulus_template',
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
            'attr': 'ec_electrode_groups',
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
    ]

    __nwbfields__ = ('experimenter',
                     'data_collection',
                     'description',
                     'experiment_description',
                     'session_id',
                     'lab',
                     'institution',
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
                     {'name': 'ec_electrodes', 'child': True},
                     {'name': 'epochs', 'child': True},
                     {'name': 'trials', 'child': True},
                     {'name': 'subject', 'child': True},
                     'epoch_tags',)

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'session_description', 'type': str,
             'doc': 'a description of the session where this data was generated'},
            {'name': 'identifier', 'type': str, 'doc': 'a unique text identifier for the file'},
            {'name': 'session_start_time', 'type': (datetime, str), 'doc': 'the start time of the recording session'},
            {'name': 'file_create_date', 'type': ('array_data', 'data', datetime, str),
             'doc': 'the time the file was created and subsequent modifications made', 'default': None},
            {'name': 'experimenter', 'type': str, 'doc': 'name of person who performed experiment', 'default': None},
            {'name': 'experiment_description', 'type': str,
             'doc': 'general description of the experiment', 'default': None},
            {'name': 'session_id', 'type': str, 'doc': 'lab-specific ID for the session', 'default': None},
            {'name': 'institution', 'type': str,
             'doc': 'institution(s) where experiment is performed', 'default': None},
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
             'doc': 'Name of the sourc_script file', 'default': None},
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
            {'name': 'epochs', 'type': Epochs,
             'doc': 'Epoch objects belonging to this NWBFile', 'default': None},
            {'name': 'epoch_tags', 'type': (tuple, list, set),
             'doc': 'A sorted list of tags used across all epochs', 'default': set()},
            {'name': 'trials', 'type': DynamicTable,
             'doc': 'A table containing trial data', 'default': None},
            {'name': 'modules', 'type': (list, tuple),
             'doc': 'ProcessingModule objects belonging to this NWBFile', 'default': None},
            {'name': 'ec_electrodes', 'type': (ElectrodeTable, Iterable),
             'doc': 'the ElectrodeTable that belongs to this NWBFile', 'default': None},
            {'name': 'ec_electrode_groups', 'type': Iterable,
             'doc': 'the ElectrodeGroups that belong to this NWBFile', 'default': None},
            {'name': 'ic_electrodes', 'type': (list, tuple),
             'doc': 'IntracellularElectrodes that belong to this NWBFile', 'default': None},
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
        if isinstance(self.__session_start_time, str):
            self.__session_start_time = parse_date(self.__session_start_time)
        self.__file_create_date = getargs('file_create_date', kwargs)
        if self.__file_create_date is None:
            self.__file_create_date = datetime.utcnow().isoformat() + "Z"
        if isinstance(self.__file_create_date, datetime):
            self.__file_create_date = [self.__file_create_date]
        elif isinstance(self.__file_create_date, str):
            self.__file_create_date = [parse_date(self.__file_create_date)]

        self.acquisition = getargs('acquisition', kwargs)
        self.stimulus = getargs('stimulus', kwargs)
        self.stimulus_template = getargs('stimulus_template', kwargs)

        self.modules = getargs('modules', kwargs)
        epochs = getargs('epochs', kwargs)
        if epochs is not None:
            self.epochs = epochs
        self.epoch_tags = getargs('epoch_tags', kwargs)

        trials = getargs('trials', kwargs)
        if trials is not None:
            self.trials = trials
        self.ec_electrodes = getargs('ec_electrodes', kwargs)
        self.ec_electrode_groups = getargs('ec_electrode_groups', kwargs)
        self.devices = getargs('devices', kwargs)

        self.ic_electrodes = getargs('ic_electrodes', kwargs)
        self.imaging_planes = getargs('imaging_planes', kwargs)
        self.ogen_sites = getargs('ogen_sites', kwargs)

        self.subject = getargs('subject', kwargs)

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

    @docval(*get_docval(ElectrodeTable.add_row))
    def add_electrode(self, **kwargs):
        if self.ec_electrodes is None:
            self.ec_electrodes = ElectrodeTable('electrodes')
        return call_docval_func(self.ec_electrodes.add_row, kwargs)

    @docval({'name': 'region', 'type': (slice, list, tuple, RegionReference), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'electrodes'})
    def create_electrode_table_region(self, **kwargs):
        if self.ec_electrodes is None:
            msg = "no electrodes available. add electrodes before creating a region"
            raise RuntimeError(msg)
        region = getargs('region', kwargs)
        desc = getargs('description', kwargs)
        name = getargs('name', kwargs)
        return ElectrodeTableRegion(self.ec_electrodes, region, desc, name)

    @docval(*get_docval(Epochs.add_epoch))
    def create_epoch(self, **kwargs):
        """
        Creates a new Epoch object. Epochs are used to track intervals
        in an experiment, such as exposure to a certain type of stimuli
        (an interval where orientation gratings are shown, or of
        sparse noise) or a different paradigm (a rat exploring an
        enclosure versus sleeping between explorations)
        """
        if self.epochs is None:
            self.epochs = Epochs(self.source)
        self.epoch_tags.update(kwargs.get('tags', list()))
        call_docval_func(self.epochs.add_epoch, kwargs)

    def __check_trials(self):
        if self.trials is None:
            self.trials = DynamicTable('trials', 'autogenerated by PyNWB API', 'data about experimental trials')
            self.trials.add_column('start', 'the start time of each trial')
            self.trials.add_column('end', 'the end time of each trial')

    @docval(*get_docval(DynamicTable.add_column))
    def add_trial_column(self, **kwargs):
        """
        Add a column to the trial table. See DynamicTable.add_column
        for more details
        """
        self.__check_trials()
        call_docval_func(self.trials.add_column, kwargs)

    @docval(*get_docval(DynamicTable.add_row))
    def add_trial(self, **kwargs):
        """
        Add a trial to the trial table. See DynamicTable.add_row for
        more details.

        Required fields are *start*, *end*, and any columns that have
        been added (through calls to `add_trial_columns`).
        """
        self.__check_trials()
        call_docval_func(self.trials.add_row, kwargs)

    @docval({'name': 'electrode_table', 'type': ElectrodeTable, 'doc': 'the ElectrodeTable for this file'})
    def set_electrode_table(self, **kwargs):
        if self.ec_electrodes is not None:
            msg = 'ElectrodeTable already exists, cannot overwrite'
            raise ValueError(msg)
        electrode_table = getargs('electrode_table', kwargs)
        self.ec_electrodes = electrode_table
