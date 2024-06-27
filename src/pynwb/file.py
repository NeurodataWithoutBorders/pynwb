from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from collections.abc import Iterable
from warnings import warn
import copy as _copy

import numpy as np
import pandas as pd

from hdmf.common import DynamicTableRegion, DynamicTable
from hdmf.container import HERDManager
from hdmf.utils import docval, getargs, get_docval, popargs, popargs_to_dict, AllowPositional

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, ProcessingModule
from .device import Device
from .epoch import TimeIntervals
from .ecephys import ElectrodeGroup
from .icephys import (IntracellularElectrode, SweepTable, PatchClampSeries, IntracellularRecordingsTable,
                      SimultaneousRecordingsTable, SequentialRecordingsTable, RepetitionsTable,
                      ExperimentalConditionsTable)
from .image import Images
from .ophys import ImagingPlane
from .ogen import OptogeneticStimulusSite
from .misc import Units
from .core import NWBContainer, NWBDataInterface, MultiContainerInterface, ScratchData, LabelledDict


def _not_parent(arg):
    return arg['name'] != 'parent'


@register_class('LabMetaData', CORE_NAMESPACE)
class LabMetaData(NWBContainer):
    """
    Container for storing lab-specific meta-data

    The LabMetaData class serves as a base type for defining lab specific meta-data.
    To define your own lab-specific metadata, create a Neurodata Extension (NDX) for
    NWB that defines the data to add. Using the LabMetaData container as a base type
    makes it easy to add your data to an NWBFile without having to modify the NWBFile
    type itself, since adding of LabMetaData is already implemented. For more details
    on how to create an extension see the
    :nwb_overview:`Extending NWB <extensions_tutorial/extensions_tutorial_home.html>`
    tutorial.
    """

    @docval({'name': 'name', 'type': str, 'doc': 'name of lab metadata'})
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register_class('Subject', CORE_NAMESPACE)
class Subject(NWBContainer):
    """Subject information and metadata."""

    __nwbfields__ = (
        'age',
        "age__reference",
        'description',
        'genotype',
        'sex',
        'species',
        'subject_id',
        'weight',
        'date_of_birth',
        'strain'
    )

    @docval(
        {
            "name": "age",
            "type": (str, timedelta),
            "doc": 'The age of the subject. The ISO 8601 Duration format is recommended, e.g., "P90D" for 90 days old.'
                   'A timedelta will automatically be converted to The ISO 8601 Duration format.',
            "default": None,
        },
        {
            "name": "age__reference",
            "type": str,
            "doc": "Age is with reference to this event. Can be 'birth' or 'gestational'. If reference is omitted, "
                   "then 'birth' is implied. Value can be None when read from an NWB file with schema version "
                   "2.0 to 2.5 where age__reference is missing.",
            "default": "birth",
        },
        {
            "name": "description",
            "type": str,
            "doc": 'A description of the subject, e.g., "mouse A10".',
            "default": None,
        },
        {'name': 'genotype', 'type': str,
         'doc': 'The genotype of the subject, e.g., "Sst-IRES-Cre/wt;Ai32(RCL-ChR2(H134R)_EYFP)/wt".',
         'default': None},
        {'name': 'sex', 'type': str,
         'doc': ('The sex of the subject. Using "F" (female), "M" (male), "U" (unknown), or "O" (other) '
                 'is recommended.'), 'default': None},
        {'name': 'species', 'type': str,
         'doc': 'The species of the subject. The formal latin binomal name is recommended, e.g., "Mus musculus"',
         'default': None},
        {'name': 'subject_id', 'type': str, 'doc': 'A unique identifier for the subject, e.g., "A10"',
         'default': None},
        {'name': 'weight', 'type': (float, str),
         'doc': ('The weight of the subject, including units. Using kilograms is recommended. e.g., "0.02 kg". '
                 'If a float is provided, then the weight will be stored as "[value] kg".'),
         'default': None},
        {'name': 'date_of_birth', 'type': datetime, 'default': None,
         'doc': 'The datetime of the date of birth. May be supplied instead of age.'},
        {'name': 'strain', 'type': str, 'doc': 'The strain of the subject, e.g., "C57BL/6J"', 'default': None},
    )
    def __init__(self, **kwargs):
        keys_to_set = (
            "age",
            "age__reference",
            "description",
            "genotype",
            "sex",
            "species",
            "subject_id",
            "weight",
            "date_of_birth",
            "strain",
        )
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(name="subject", **kwargs)

        # NOTE when the Subject I/O mapper (see pynwb.io.file.py) reads an age__reference value of None from an
        # NWB 2.0-2.5 file, it sets the value to "unspecified" so that when Subject.__init__ is called, the incoming
        # age__reference value is NOT replaced by the default value ("birth") specified in the docval.
        # then we replace "unspecified" with None here. the user will never see the value "unspecified".
        # the ONLY way that age__reference can now be None is if it is read as None from an NWB 2.0-2.5 file.
        if self._in_construct_mode and args_to_set["age__reference"] == "unspecified":
            args_to_set["age__reference"] = None
        elif args_to_set["age__reference"] not in ("birth", "gestational"):
            raise ValueError("age__reference, if supplied, must be 'birth' or 'gestational'.")

        weight = args_to_set['weight']
        if isinstance(weight, float):
            args_to_set['weight'] = str(weight) + ' kg'

        if isinstance(args_to_set["age"], timedelta):
            args_to_set["age"] = pd.Timedelta(args_to_set["age"]).isoformat()

        date_of_birth = args_to_set['date_of_birth']
        if date_of_birth and date_of_birth.tzinfo is None:
            args_to_set['date_of_birth'] = _add_missing_timezone(date_of_birth)

        for key, val in args_to_set.items():
            setattr(self, key, val)


@register_class('NWBFile', CORE_NAMESPACE)
class NWBFile(MultiContainerInterface, HERDManager):
    """
    A representation of an NWB file.
    """

    __clsconf__ = [
        {
            'attr': 'acquisition',
            'add': '_add_acquisition_internal',
            'type': (NWBDataInterface, DynamicTable),
            'get': 'get_acquisition'
        },
        {
            'attr': 'analysis',
            'add': 'add_analysis',
            'type': (NWBContainer, DynamicTable),
            'get': 'get_analysis'
        },
        {
            'attr': 'scratch',
            'add': '_add_scratch',
            'type': (DynamicTable, NWBContainer, ScratchData),
            'get': '_get_scratch'
        },
        {
            'attr': 'stimulus',
            'add': '_add_stimulus_internal',
            'type': (NWBDataInterface, DynamicTable),
            'get': 'get_stimulus'
        },
        {
            'attr': 'stimulus_template',
            'add': '_add_stimulus_template_internal',
            'type': (TimeSeries, Images),
            'get': 'get_stimulus_template'
        },
        {
            'attr': 'processing',
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
            'attr': 'icephys_electrodes',
            'add': 'add_icephys_electrode',
            'type': IntracellularElectrode,
            'create': 'create_icephys_electrode',
            'get': 'get_icephys_electrode'
        },
        {
            'attr': 'ogen_sites',
            'add': 'add_ogen_site',
            'type': OptogeneticStimulusSite,
            'create': 'create_ogen_site',
            'get': 'get_ogen_site'
        },
        {
            'attr': 'intervals',
            'add': 'add_time_intervals',
            'type': TimeIntervals,
            'create': 'create_time_intervals',
            'get': 'get_time_intervals'
        },
        {
            'attr': 'lab_meta_data',
            'add': 'add_lab_meta_data',
            'type': LabMetaData,
            'create': 'create_lab_meta_data',
            'get': 'get_lab_meta_data'
        }
    ]

    __nwbfields__ = ({'name': 'session_description', 'settable': False},
                     {'name': 'identifier', 'settable': False},
                     {'name': 'session_start_time', 'settable': False},
                     {'name': 'timestamps_reference_time', 'settable': False},
                     {'name': 'file_create_date', 'settable': False},
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
                     'epoch_tags',
                     # icephys_filtering is temporary. /intracellular_ephys/filtering dataset will be deprecated
                     {'name': 'icephys_filtering', 'settable': False},
                     {'name': 'intracellular_recordings', 'child': True,
                      'required_name': 'intracellular_recordings',
                      'doc': 'IntracellularRecordingsTable table to group together a stimulus and response '
                             'from a single intracellular electrode and a single simultaneous recording.'},
                     {'name': 'icephys_simultaneous_recordings',
                      'child': True,
                      'required_name': 'simultaneous_recordings',
                      'doc': 'SimultaneousRecordingsTable table for grouping different intracellular recordings from'
                             'the IntracellularRecordingsTable table together that were recorded simultaneously '
                             'from different electrodes'},
                     {'name': 'icephys_sequential_recordings',
                      'child': True,
                      'required_name': 'sequential_recordings',
                      'doc': 'A table for grouping different simultaneous intracellular recording from the '
                             'SimultaneousRecordingsTable table together. This is typically used to group '
                             'together simultaneous recordings where the a sequence of stimuli of the same '
                             'type with varying parameters have been presented in a sequence.'},
                     {'name': 'icephys_repetitions',
                      'child': True,
                      'required_name': 'repetitions',
                      'doc': 'A table for grouping different intracellular recording sequential recordings together.'
                             'With each SweepSequence typically representing a particular type of stimulus, the '
                             'RepetitionsTable table is typically used to group sets of stimuli applied in sequence.'},
                     {'name': 'icephys_experimental_conditions',
                      'child': True,
                      'required_name': 'experimental_conditions',
                      'doc': 'A table for grouping different intracellular recording repetitions together that '
                             'belong to the same experimental experimental_conditions.'})

    @docval({'name': 'session_description', 'type': str,
             'doc': 'a description of the session where this data was generated'},
            {'name': 'identifier', 'type': str, 'doc': 'a unique text identifier for the file'},
            {'name': 'session_start_time', 'type': datetime, 'doc': 'the start date and time of the recording session'},
            {'name': 'file_create_date', 'type': ('array_data', datetime),
             'doc': 'the date and time the file was created and subsequent modifications made', 'default': None},
            {'name': 'timestamps_reference_time', 'type': datetime,
             'doc': 'date and time corresponding to time zero of all timestamps; defaults to value '
                    'of session_start_time', 'default': None},
            {'name': 'experimenter', 'type': (tuple, list, str),
             'doc': 'name of person who performed experiment', 'default': None},
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
            {'name': 'related_publications', 'type': (tuple, list, str),
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
            {'name': 'analysis', 'type': (list, tuple),
             'doc': 'result of analysis', 'default': None},
            {'name': 'stimulus', 'type': (list, tuple),
             'doc': 'Stimulus TimeSeries, DynamicTable, or NWBDataInterface objects belonging to this NWBFile',
             'default': None},
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
            {'name': 'intervals', 'type': (list, tuple),
             'doc': 'any TimeIntervals tables storing time intervals', 'default': None},
            {'name': 'units', 'type': Units,
             'doc': 'A table containing unit metadata', 'default': None},
            {'name': 'processing', 'type': (list, tuple),
             'doc': 'ProcessingModule objects belonging to this NWBFile', 'default': None},
            {'name': 'lab_meta_data', 'type': (list, tuple), 'default': None,
             'doc': 'an extension that contains lab-specific meta-data'},
            {'name': 'electrodes', 'type': DynamicTable,
             'doc': 'the ElectrodeTable that belongs to this NWBFile', 'default': None},
            {'name': 'electrode_groups', 'type': Iterable,
             'doc': 'the ElectrodeGroups that belong to this NWBFile', 'default': None},
            {'name': 'ic_electrodes', 'type': (list, tuple),
             'doc': 'DEPRECATED use icephys_electrodes parameter instead. '
                    'IntracellularElectrodes that belong to this NWBFile', 'default': None},
            {'name': 'sweep_table', 'type': SweepTable,
             'doc': 'the SweepTable that belong to this NWBFile', 'default': None},
            {'name': 'imaging_planes', 'type': (list, tuple),
             'doc': 'ImagingPlanes that belong to this NWBFile', 'default': None},
            {'name': 'ogen_sites', 'type': (list, tuple),
             'doc': 'OptogeneticStimulusSites that belong to this NWBFile', 'default': None},
            {'name': 'devices', 'type': (list, tuple),
             'doc': 'Device objects belonging to this NWBFile', 'default': None},
            {'name': 'subject', 'type': Subject,
             'doc': 'subject metadata', 'default': None},
            {'name': 'scratch', 'type': (list, tuple),
             'doc': 'scratch data', 'default': None},
            {'name': 'icephys_electrodes', 'type': (list, tuple),
             'doc': 'IntracellularElectrodes that belong to this NWBFile.', 'default': None},
            {'name': 'icephys_filtering', 'type': str, 'default': None,
             'doc': '[DEPRECATED] Use IntracellularElectrode.filtering instead. Description of filtering used.'},
            {'name': 'intracellular_recordings', 'type': IntracellularRecordingsTable, 'default': None,
             'doc': 'the IntracellularRecordingsTable table that belongs to this NWBFile'},
            {'name': 'icephys_simultaneous_recordings', 'type': SimultaneousRecordingsTable, 'default': None,
             'doc': 'the SimultaneousRecordingsTable table that belongs to this NWBFile'},
            {'name': 'icephys_sequential_recordings', 'type': SequentialRecordingsTable, 'default': None,
             'doc': 'the SequentialRecordingsTable table that belongs to this NWBFile'},
            {'name': 'icephys_repetitions', 'type': RepetitionsTable, 'default': None,
             'doc': 'the RepetitionsTable table that belongs to this NWBFile'},
            {'name': 'icephys_experimental_conditions', 'type': ExperimentalConditionsTable, 'default': None,
             'doc': 'the ExperimentalConditionsTable table that belongs to this NWBFile'})
    def __init__(self, **kwargs):
        keys_to_set = [
            'session_description',
            'identifier',
            'session_start_time',
            'experimenter',
            'file_create_date',
            'ic_electrodes',
            'icephys_electrodes',
            'related_publications',
            'timestamps_reference_time',
            'acquisition',
            'analysis',
            'stimulus',
            'stimulus_template',
            'keywords',
            'processing',
            'epoch_tags',
            'electrodes',
            'electrode_groups',
            'devices',
            'imaging_planes',
            'ogen_sites',
            'intervals',
            'subject',
            'sweep_table',
            'lab_meta_data',
            'epochs',
            'trials',
            'invalid_times',
            'units',
            'scratch',
            'experiment_description',
            'session_id',
            'lab',
            'institution',
            'data_collection',
            'notes',
            'pharmacology',
            'protocol',
            'slices',
            'source_script',
            'source_script_file_name',
            'surgery',
            'virus',
            'stimulus_notes',
            'icephys_filtering',  # DEPRECATION warning will be raised in the setter when calling setattr in the loop
            'intracellular_recordings',
            'icephys_simultaneous_recordings',
            'icephys_sequential_recordings',
            'icephys_repetitions',
            'icephys_experimental_conditions'
        ]
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        kwargs['name'] = 'root'
        super().__init__(**kwargs)

        # add timezone to session_start_time if missing
        session_start_time = args_to_set['session_start_time']
        if session_start_time.tzinfo is None:
            args_to_set['session_start_time'] = _add_missing_timezone(session_start_time)

        # set timestamps_reference_time to session_start_time if not provided
        # if provided, ensure that it has a timezone
        timestamps_reference_time = args_to_set['timestamps_reference_time']
        if timestamps_reference_time is None:
            args_to_set['timestamps_reference_time'] = args_to_set['session_start_time']
        elif timestamps_reference_time.tzinfo is None:
            raise ValueError("'timestamps_reference_time' must be a timezone-aware datetime object.")

        # convert file_create_date to list and add timezone if missing
        file_create_date = args_to_set['file_create_date']
        if file_create_date is None:
            file_create_date = datetime.now(tzlocal())
        if isinstance(file_create_date, datetime):
            file_create_date = [file_create_date]
        args_to_set['file_create_date'] = list(map(_add_missing_timezone, file_create_date))

        # backwards-compatibility code for ic_electrodes / icephys_electrodes
        icephys_electrodes = args_to_set['icephys_electrodes']
        ic_electrodes = args_to_set['ic_electrodes']
        if icephys_electrodes is None and ic_electrodes is not None:
            warn("Use of the ic_electrodes parameter is deprecated. "
                 "Use the icephys_electrodes parameter instead", DeprecationWarning)
            args_to_set['icephys_electrodes'] = ic_electrodes
        args_to_set.pop('ic_electrodes')  # do not set this arg

        # convert single experimenter to tuple
        experimenter = args_to_set['experimenter']
        if isinstance(experimenter, str):
            args_to_set['experimenter'] = (experimenter,)

        # convert single related_publications to tuple
        related_pubs = args_to_set['related_publications']
        if isinstance(related_pubs, str):
            args_to_set['related_publications'] = (related_pubs,)

        # ensure source_script is provided if source_script_file_name is provided
        if args_to_set['source_script'] is None and args_to_set['source_script_file_name'] is not None:
            raise ValueError("'source_script' cannot be None when 'source_script_file_name' is set")

        # these attributes have no setters and can only be set using self.fields
        keys_to_set_via_fields = (
            'session_description',
            'identifier',
            'session_start_time',
            'timestamps_reference_time',
            'file_create_date'
        )
        args_to_set_via_fields = popargs_to_dict(keys_to_set_via_fields, args_to_set)

        for key, val in args_to_set_via_fields.items():
            self.fields[key] = val

        for key, val in args_to_set.items():
            setattr(self, key, val)

        self.__obj = None

    def all_children(self):
        stack = [self]
        ret = list()
        self.__obj = LabelledDict(label='all_objects', key_attr='object_id')
        while len(stack):
            n = stack.pop()
            ret.append(n)
            if n.object_id is not None:
                self.__obj[n.object_id] = n
            else:
                warn('%s "%s" does not have an object_id' % (n.neurodata_type, n.name))
            if hasattr(n, 'children'):
                for c in n.children:
                    stack.append(c)
        return ret

    @property
    def objects(self):
        if self.__obj is None:
            self.all_children()
        return self.__obj

    @property
    def modules(self):
        warn("NWBFile.modules has been replaced by NWBFile.processing.", DeprecationWarning)
        return self.processing

    @property
    def ec_electrode_groups(self):
        warn("NWBFile.ec_electrode_groups has been replaced by NWBFile.electrode_groups.", DeprecationWarning)
        return self.electrode_groups

    @property
    def ec_electrodes(self):
        warn("NWBFile.ec_electrodes has been replaced by NWBFile.electrodes.", DeprecationWarning)
        return self.electrodes

    @property
    def ic_electrodes(self):
        warn("NWBFile.ic_electrodes has been replaced by NWBFile.icephys_electrodes.", DeprecationWarning)
        return self.icephys_electrodes

    @property
    def icephys_filtering(self):
        return self.fields.get('icephys_filtering')

    @icephys_filtering.setter
    def icephys_filtering(self, val):
        if val is not None:
            warn("Use of icephys_filtering is deprecated. Use the IntracellularElectrode.filtering field instead",
                 DeprecationWarning)
            self.fields['icephys_filtering'] = val

    def add_ic_electrode(self, *args, **kwargs):
        """
        This method is deprecated and will be removed in future versions. Please
        use :py:meth:`~pynwb.file.NWBFile.add_icephys_electrode` instead
        """
        warn("NWBFile.add_ic_electrode has been replaced by NWBFile.add_icephys_electrode.", DeprecationWarning)
        return self.add_icephys_electrode(*args, **kwargs)

    def create_ic_electrode(self, *args, **kwargs):
        """
        This method is deprecated and will be removed in future versions. Please
        use :py:meth:`~pynwb.file.NWBFile.create_icephys_electrode` instead
        """
        warn("NWBFile.create_ic_electrode has been replaced by NWBFile.create_icephys_electrode.", DeprecationWarning)
        return self.create_icephys_electrode(*args, **kwargs)

    def get_ic_electrode(self, *args, **kwargs):
        """
        This method is deprecated and will be removed in future versions. Please
        use :py:meth:`~pynwb.file.NWBFile.get_icephys_electrode` instead
        """
        warn("NWBFile.get_ic_electrode has been replaced by NWBFile.get_icephys_electrode.", DeprecationWarning)
        return self.get_icephys_electrode(*args, **kwargs)

    def __check_epochs(self):
        if self.epochs is None:
            self.epochs = TimeIntervals(name='epochs', description='experimental epochs')

    @docval(*get_docval(TimeIntervals.add_column), allow_extra=True)
    def add_epoch_column(self, **kwargs):
        """
        Add a column to the epoch table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_column` for more details
        """
        self.__check_epochs()
        self.epoch_tags.update(kwargs.pop('tags', list()))
        self.epochs.add_column(**kwargs)

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
        self.epochs.add_interval(**kwargs)

    def __check_electrodes(self):
        if self.electrodes is None:
            self.electrodes = ElectrodeTable()

    @docval(*get_docval(DynamicTable.add_column), allow_extra=True)
    def add_electrode_column(self, **kwargs):
        """
        Add a column to the electrode table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_column` for more details
        """
        self.__check_electrodes()
        self.electrodes.add_column(**kwargs)

    @docval({'name': 'x', 'type': float, 'doc': 'the x coordinate of the position (+x is posterior)',
             'default': None},
            {'name': 'y', 'type': float, 'doc': 'the y coordinate of the position (+y is inferior)', 'default': None},
            {'name': 'z', 'type': float, 'doc': 'the z coordinate of the position (+z is right)', 'default': None},
            {'name': 'imp', 'type': float, 'doc': 'the impedance of the electrode, in ohms', 'default': None},
            {'name': 'location', 'type': str,
             'doc': 'the location of electrode within the subject e.g. brain region. Required.',
             'default': None},
            {'name': 'filtering', 'type': str,
             'doc': 'description of hardware filtering, including the filter name and frequency cutoffs',
             'default': None},
            {'name': 'group', 'type': ElectrodeGroup,
             'doc': 'the ElectrodeGroup object to add to this NWBFile. Required.',
             'default': None},
            {'name': 'id', 'type': int, 'doc': 'a unique identifier for the electrode', 'default': None},
            {'name': 'rel_x', 'type': float, 'doc': 'the x coordinate within the electrode group', 'default': None},
            {'name': 'rel_y', 'type': float, 'doc': 'the y coordinate within the electrode group', 'default': None},
            {'name': 'rel_z', 'type': float, 'doc': 'the z coordinate within the electrode group', 'default': None},
            {'name': 'reference', 'type': str, 'doc': 'Description of the reference electrode and/or reference scheme\
                used for this  electrode, e.g.,"stainless steel skull screw" or "online common average referencing". ',
                'default': None},
            {'name': 'enforce_unique_id', 'type': bool, 'doc': 'enforce that the id in the table must be unique',
             'default': True},
            allow_extra=True,
            allow_positional=AllowPositional.WARNING)
    def add_electrode(self, **kwargs):
        """
        Add an electrode to the electrodes table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_row` for more details.

        Required fields are *location* and
        *group* and any columns that have been added
        (through calls to `add_electrode_columns`).
        """
        self.__check_electrodes()
        d = _copy.copy(kwargs['data']) if kwargs.get('data') is not None else kwargs

        # NOTE location and group are required arguments. in PyNWB 2.1.0 we made x, y, z optional arguments, and
        # in order to avoid breaking API changes, the order of the arguments needed to be maintained even though
        # these optional arguments came before the required arguments, so in docval these required arguments are
        # displayed as optional when really they are required. this should be changed when positional arguments
        # are not allowed
        if not d['location']:
            raise ValueError("The 'location' argument is required when creating an electrode.")
        if not kwargs['group']:
            raise ValueError("The 'group' argument is required when creating an electrode.")
        if d.get('group_name', None) is None:
            d['group_name'] = d['group'].name

        new_cols = [('x', 'the x coordinate of the position (+x is posterior)'),
                    ('y', 'the y coordinate of the position (+y is inferior)'),
                    ('z', 'the z coordinate of the position (+z is right)'),
                    ('imp', 'the impedance of the electrode, in ohms'),
                    ('filtering', 'description of hardware filtering, including the filter name and frequency cutoffs'),
                    ('rel_x', 'the x coordinate within the electrode group'),
                    ('rel_y', 'the y coordinate within the electrode group'),
                    ('rel_z', 'the z coordinate within the electrode group'),
                    ('reference', 'Description of the reference electrode and/or reference scheme used for this \
                        electrode, e.g.,"stainless steel skull screw" or "online common average referencing".')
                    ]

        # add column if the arg is supplied and column does not yet exist
        # do not pass arg to add_row if arg is not supplied
        for col_name, col_doc in new_cols:
            if kwargs[col_name] is not None:
                if col_name not in self.electrodes:
                    self.electrodes.add_column(col_name, col_doc)
            else:
                d.pop(col_name)  # remove args from d if not set

        self.electrodes.add_row(**d)

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
        return DynamicTableRegion(name=name, data=region, description=desc, table=self.electrodes)

    def __check_units(self):
        if self.units is None:
            self.units = Units(name='units', description='Autogenerated by NWBFile')

    @docval(*get_docval(Units.add_column), allow_extra=True)
    def add_unit_column(self, **kwargs):
        """
        Add a column to the unit table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_column` for more details
        """
        self.__check_units()
        self.units.add_column(**kwargs)

    @docval(*get_docval(Units.add_unit), allow_extra=True)
    def add_unit(self, **kwargs):
        """
        Add a unit to the unit table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_row` for more details.

        """
        self.__check_units()
        self.units.add_unit(**kwargs)

    def __check_trials(self):
        if self.trials is None:
            self.trials = TimeIntervals(name='trials', description='experimental trials')

    @docval(*get_docval(DynamicTable.add_column), allow_extra=True)
    def add_trial_column(self, **kwargs):
        """
        Add a column to the trial table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_column` for more details
        """
        self.__check_trials()
        self.trials.add_column(**kwargs)

    @docval(*get_docval(TimeIntervals.add_interval), allow_extra=True)
    def add_trial(self, **kwargs):
        """
        Add a trial to the trial table.
        See :py:meth:`~pynwb.epoch.TimeIntervals.add_interval` for more details.

        Required fields are *start_time*, *stop_time*, and any columns that have
        been added (through calls to `add_trial_columns`).
        """
        self.__check_trials()
        self.trials.add_interval(**kwargs)

    def __check_invalid_times(self):
        if self.invalid_times is None:
            self.invalid_times = TimeIntervals(
                name='invalid_times',
                description='time intervals to be removed from analysis'
            )

    @docval(*get_docval(DynamicTable.add_column), allow_extra=True)
    def add_invalid_times_column(self, **kwargs):
        """
        Add a column to the invalid times table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_column` for more details
        """
        self.__check_invalid_times()
        self.invalid_times.add_column(**kwargs)

    @docval(*get_docval(TimeIntervals.add_interval), allow_extra=True)
    def add_invalid_time_interval(self, **kwargs):
        """
        Add a time interval to the invalid times table.
        See :py:meth:`~hdmf.common.table.DynamicTable.add_row` for more details.

        Required fields are *start_time*, *stop_time*, and any columns that have
        been added (through calls to `add_invalid_times_columns`).
        """
        self.__check_invalid_times()
        self.invalid_times.add_interval(**kwargs)

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

    @docval({'name': 'nwbdata', 'type': (NWBDataInterface, DynamicTable)},
            {'name': 'use_sweep_table', 'type': bool, 'default': False, 'doc': 'Use the deprecated SweepTable'})
    def add_acquisition(self, **kwargs):
        nwbdata = popargs('nwbdata', kwargs)
        self._add_acquisition_internal(nwbdata)
        use_sweep_table = popargs('use_sweep_table', kwargs)
        if use_sweep_table:
            self._update_sweep_table(nwbdata)

    @docval({'name': 'stimulus', 'type': (TimeSeries, DynamicTable, NWBDataInterface), 'default': None,
             'doc': 'The stimulus presentation data to add to this NWBFile.'},
            {'name': 'use_sweep_table', 'type': bool, 'default': False, 'doc': 'Use the deprecated SweepTable'},
            {'name': 'timeseries', 'type': TimeSeries, 'default': None,
             'doc': 'The "timeseries" keyword argument is deprecated. Use the "nwbdata" argument instead.'},)
    def add_stimulus(self, **kwargs):
        stimulus, timeseries = popargs('stimulus', 'timeseries', kwargs)
        if stimulus is None and timeseries is None:
            raise ValueError(
                "The 'stimulus' keyword argument is required. The 'timeseries' keyword argument can be "
                "provided for backwards compatibility but is deprecated in favor of 'stimulus' and will be "
                "removed in PyNWB 3.0."
            )
        # TODO remove this support in PyNWB 3.0
        if timeseries is not None:
            warn("The 'timeseries' keyword argument is deprecated and will be removed in PyNWB 3.0. "
                 "Use the 'stimulus' argument instead.", DeprecationWarning)
            if stimulus is None:
                stimulus = timeseries
        self._add_stimulus_internal(stimulus)
        use_sweep_table = popargs('use_sweep_table', kwargs)
        if use_sweep_table:
            self._update_sweep_table(stimulus)

    @docval({'name': 'timeseries', 'type': (TimeSeries, Images)},
            {'name': 'use_sweep_table', 'type': bool, 'default': False, 'doc': 'Use the deprecated SweepTable'})
    def add_stimulus_template(self, **kwargs):
        timeseries = popargs('timeseries', kwargs)
        self._add_stimulus_template_internal(timeseries)
        use_sweep_table = popargs('use_sweep_table', kwargs)
        if use_sweep_table:
            self._update_sweep_table(timeseries)

    @docval(returns='The NWBFile.intracellular_recordings table', rtype=IntracellularRecordingsTable)
    def get_intracellular_recordings(self):
        """
        Get the NWBFile.intracellular_recordings table.

        In contrast to NWBFile.intracellular_recordings, this function will create the
        IntracellularRecordingsTable table if not yet done, whereas NWBFile.intracellular_recordings
        will return None if the table is currently not being used.
        """
        if self.intracellular_recordings is None:
            self.intracellular_recordings = IntracellularRecordingsTable()
        return self.intracellular_recordings

    @docval(*get_docval(IntracellularRecordingsTable.add_recording),
            returns='Integer index of the row that was added to IntracellularRecordingsTable',
            rtype=int,
            allow_extra=True)
    def add_intracellular_recording(self, **kwargs):
        """
        Add a intracellular recording to the intracellular_recordings table. If the
        electrode, stimulus, and/or response do not exist yet in the NWBFile, then
        they will be added to this NWBFile before adding them to the table.

        Note: For more complex organization of intracellular recordings you may also be
        interested in the related SimultaneousRecordingsTable, SequentialRecordingsTable,
        RepetitionsTable, and ExperimentalConditionsTable tables and the related functions
        of NWBFile: add_icephys_simultaneous_recording, add_icephys_sequential_recording,
        add_icephys_repetition, and add_icephys_experimental_condition.
        """
        # Add the stimulus, response, and electrode to the file if they don't exist yet
        stimulus, response, electrode = getargs('stimulus', 'response', 'electrode', kwargs)
        if (stimulus is not None and
                (stimulus.name not in self.stimulus and
                 stimulus.name not in self.stimulus_template)):
            self.add_stimulus(stimulus, use_sweep_table=False)
        if response is not None and response.name not in self.acquisition:
            self.add_acquisition(response, use_sweep_table=False)
        if electrode is not None and electrode.name not in self.icephys_electrodes:
            self.add_icephys_electrode(electrode)
        # make sure the intracellular recordings table exists and if not create it using get_intracellular_recordings
        # Add the recoding to the intracellular_recordings table
        return self.get_intracellular_recordings().add_recording(**kwargs)

    @docval(returns='The NWBFile.icephys_simultaneous_recordings table', rtype=SimultaneousRecordingsTable)
    def get_icephys_simultaneous_recordings(self):
        """
        Get the NWBFile.icephys_simultaneous_recordings table.

        In contrast to NWBFile.icephys_simultaneous_recordings, this function will create the
        SimultaneousRecordingsTable table if not yet done, whereas NWBFile.icephys_simultaneous_recordings
        will return None if the table is currently not being used.
        """
        if self.icephys_simultaneous_recordings is None:
            self.icephys_simultaneous_recordings = SimultaneousRecordingsTable(self.get_intracellular_recordings())
        return self.icephys_simultaneous_recordings

    @docval(*get_docval(SimultaneousRecordingsTable.add_simultaneous_recording),
            returns='Integer index of the row that was added to SimultaneousRecordingsTable',
            rtype=int,
            allow_extra=True)
    def add_icephys_simultaneous_recording(self, **kwargs):
        """
        Add a new simultaneous recording to the icephys_simultaneous_recordings table
        """
        return self.get_icephys_simultaneous_recordings().add_simultaneous_recording(**kwargs)

    @docval(returns='The NWBFile.icephys_sequential_recordings table', rtype=SequentialRecordingsTable)
    def get_icephys_sequential_recordings(self):
        """
        Get the NWBFile.icephys_sequential_recordings table.

        In contrast to NWBFile.icephys_sequential_recordings, this function will create the
        IntracellularRecordingsTable table if not yet done, whereas NWBFile.icephys_sequential_recordings
        will return None if the table is currently not being used.
        """
        if self.icephys_sequential_recordings is None:
            self.icephys_sequential_recordings = SequentialRecordingsTable(self.get_icephys_simultaneous_recordings())
        return self.icephys_sequential_recordings

    @docval(*get_docval(SequentialRecordingsTable.add_sequential_recording),
            returns='Integer index of the row that was added to SequentialRecordingsTable',
            rtype=int,
            allow_extra=True)
    def add_icephys_sequential_recording(self, **kwargs):
        """
        Add a new sequential recording to the icephys_sequential_recordings table
        """
        self.get_icephys_sequential_recordings()
        return self.icephys_sequential_recordings.add_sequential_recording(**kwargs)

    @docval(returns='The NWBFile.icephys_repetitions table', rtype=RepetitionsTable)
    def get_icephys_repetitions(self):
        """
        Get the NWBFile.icephys_repetitions table.

        In contrast to NWBFile.icephys_repetitions, this function will create the
        RepetitionsTable table if not yet done, whereas NWBFile.icephys_repetitions
        will return None if the table is currently not being used.
        """
        if self.icephys_repetitions is None:
            self.icephys_repetitions = RepetitionsTable(self.get_icephys_sequential_recordings())
        return self.icephys_repetitions

    @docval(*get_docval(RepetitionsTable.add_repetition),
            returns='Integer index of the row that was added to RepetitionsTable',
            rtype=int,
            allow_extra=True)
    def add_icephys_repetition(self, **kwargs):
        """
        Add a new repetition to the RepetitionsTable table
        """
        return self.get_icephys_repetitions().add_repetition(**kwargs)

    @docval(returns='The NWBFile.icephys_experimental_conditions table', rtype=ExperimentalConditionsTable)
    def get_icephys_experimental_conditions(self):
        """
        Get the NWBFile.icephys_experimental_conditions table.

        In contrast to NWBFile.icephys_experimental_conditions, this function will create the
        RepetitionsTable table if not yet done, whereas NWBFile.icephys_experimental_conditions
        will return None if the table is currently not being used.
        """
        if self.icephys_experimental_conditions is None:
            self.icephys_experimental_conditions = ExperimentalConditionsTable(self.get_icephys_repetitions())
        return self.icephys_experimental_conditions

    @docval(*get_docval(ExperimentalConditionsTable.add_experimental_condition),
            returns='Integer index of the row that was added to ExperimentalConditionsTable',
            rtype=int,
            allow_extra=True)
    def add_icephys_experimental_condition(self, **kwargs):
        """
        Add a new condition to the ExperimentalConditionsTable table
        """
        return self.get_icephys_experimental_conditions().add_experimental_condition(**kwargs)

    def get_icephys_meta_parent_table(self):
        """
        Get the top-most table in the intracellular ephys metadata table hierarchy that exists in this NWBFile.

        The intracellular ephys metadata consists of a hierarchy of DynamicTables, i.e.,
        experimental_conditions --> repetitions --> sequential_recordings -->
        simultaneous_recordings --> intracellular_recordings etc.
        In a given NWBFile not all tables may exist. This convenience functions returns the top-most
        table that exists in this file. E.g., if the file contains only the simultaneous_recordings
        and intracellular_recordings tables then the function would return the simultaneous_recordings table.
        Similarly, if the file contains all tables then it will return the experimental_conditions table.

        :returns: DynamicTable object or None
        """
        if self.icephys_experimental_conditions is not None:
            return self.icephys_experimental_conditions
        elif self.icephys_repetitions is not None:
            return self.icephys_repetitions
        elif self.icephys_sequential_recordings is not None:
            return self.icephys_sequential_recordings
        elif self.icephys_simultaneous_recordings is not None:
            return self.icephys_simultaneous_recordings
        elif self.intracellular_recordings is not None:
            return self.intracellular_recordings
        else:
            return None

    @docval({'name': 'data',
             'type': ('scalar_data', np.ndarray, list, tuple, pd.DataFrame, DynamicTable, NWBContainer, ScratchData),
             'doc': 'The data to add to the scratch space.'},
            {'name': 'name', 'type': str,
             'doc': 'The name of the data. Required only when passing in a scalar, numpy.ndarray, list, or tuple',
             'default': None},
            {'name': 'notes', 'type': str,
             'doc': ('Notes to add to the data. Only used when passing in numpy.ndarray, list, or tuple. This '
                     'argument is not recommended. Use the `description` argument instead.'),
             'default': None},
            {'name': 'table_description', 'type': str,
             'doc': ('Description for the internal DynamicTable used to store a pandas.DataFrame. This '
                     'argument is not recommended. Use the `description` argument instead.'),
             'default': ''},
            {'name': 'description', 'type': str,
             'doc': ('Description of the data. Required only when passing in a scalar, numpy.ndarray, '
                     'list, tuple, or pandas.DataFrame. Ignored when passing in an NWBContainer, '
                     'DynamicTable, or ScratchData object.'),
             'default': None})
    def add_scratch(self, **kwargs):
        '''Add data to the scratch space'''
        data, name, notes, table_description, description = getargs('data', 'name', 'notes', 'table_description',
                                                                    'description', kwargs)
        if notes is not None or table_description != '':
            warn('Use of the `notes` or `table_description` argument will be removed in a future version of PyNWB. '
                 'Use the `description` argument instead.', PendingDeprecationWarning)
            if description is not None:
                raise ValueError('Cannot call add_scratch with (notes or table_description) and description')

        if isinstance(data, (str, int, float, bytes, np.ndarray, list, tuple, pd.DataFrame)):
            if name is None:
                msg = ('A name is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
                       'list, tuple, or pandas.DataFrame as scratch data.')
                raise ValueError(msg)
            if isinstance(data, pd.DataFrame):
                if table_description != '':
                    description = table_description  # remove after deprecation
                if description is None:
                    msg = ('A description is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
                           'list, tuple, or pandas.DataFrame as scratch data.')
                    raise ValueError(msg)
                data = DynamicTable.from_dataframe(df=data, name=name, table_description=description)
            else:
                if notes is not None:
                    description = notes  # remove after deprecation
                if description is None:
                    msg = ('A description is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
                           'list, tuple, or pandas.DataFrame as scratch data.')
                    raise ValueError(msg)
                data = ScratchData(name=name, data=data, description=description)
        else:
            if name is not None:
                warn('The name argument is ignored when adding an NWBContainer, ScratchData, or '
                     'DynamicTable to scratch.')
            if description is not None:
                warn('The description argument is ignored when adding an NWBContainer, ScratchData, or '
                     'DynamicTable to scratch.')
        return self._add_scratch(data)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the object to get'},
            {'name': 'convert', 'type': bool, 'doc': 'return the original data, not the NWB object', 'default': True})
    def get_scratch(self, **kwargs):
        '''Get data from the scratch space'''
        name, convert = getargs('name', 'convert', kwargs)
        ret = self._get_scratch(name)
        if convert:
            if isinstance(ret, DynamicTable):
                ret = ret.to_dataframe()
            elif isinstance(ret, ScratchData):
                ret = np.asarray(ret.data)
        return ret

    def copy(self):
        """
        Shallow copy of an NWB file.
        Useful for linking across files.
        """
        kwargs = self.fields.copy()
        for key in self.fields:
            if isinstance(self.fields[key], LabelledDict):
                kwargs[key] = list(self.fields[key].values())

        # HDF5 object references cannot point to objects external to the file. Both DynamicTables such as TimeIntervals
        # contain such object references and types such as ElectricalSeries contain references to DynamicTables.
        # Below, copy the table and link to the columns so that object references work.
        fields_to_copy = ['electrodes', 'epochs', 'trials', 'units', 'sweep_table', 'invalid_times']
        for field in fields_to_copy:
            if field in kwargs:
                if isinstance(self.fields[field], DynamicTable):
                    kwargs[field] = self.fields[field].copy()
                else:
                    warn('Cannot copy child of NWBFile that is not a DynamicTable: %s' % field)

        # handle dictionaries of DynamicTables
        dt_to_copy = ['scratch', 'intervals']
        for dt in dt_to_copy:
            if dt in kwargs:
                kwargs[dt] = [v.copy() if isinstance(v, DynamicTable) else v for v in kwargs[dt]]

        return NWBFile(**kwargs)


def _add_missing_timezone(date):
    """
    Add local timezone information on a datetime object if it is missing.
    """
    if not isinstance(date, datetime):
        raise ValueError("require datetime object")
    if date.tzinfo is None:
        warn("Date is missing timezone information. Updating to local timezone.", stacklevel=2)
        return date.replace(tzinfo=tzlocal())
    return date


def _tablefunc(table_name, description, columns):
    t = DynamicTable(name=table_name, description=description)
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
                      [('location', 'the location of channel within the subject e.g. brain region'),
                       ('group', 'a reference to the ElectrodeGroup this electrode is a part of'),
                       ('group_name', 'the name of the ElectrodeGroup this electrode is a part of')
                       ]
                      )


def TrialTable(name='trials', description='metadata about experimental trials'):
    return _tablefunc(name, description, ['start_time', 'stop_time'])


def InvalidTimesTable(name='invalid_times', description='time intervals to be removed from analysis'):
    return _tablefunc(name, description, ['start_time', 'stop_time'])
