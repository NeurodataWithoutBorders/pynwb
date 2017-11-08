from datetime import datetime
from dateutil.parser import parse as parse_date
from collections import Iterable

from .form.utils import docval, getargs, fmt_docval_args, call_docval_func, get_docval
from .form import Container

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, ProcessingModule
from .epoch import Epoch
from .ecephys import ElectrodeTable, ElectrodeGroup, Device
from .icephys import IntracellularElectrode
from .ophys import ImagingPlane
from .core import NWBContainer


def _not_parent(arg):
    return arg['name'] != 'parent'


@register_class('Image', CORE_NAMESPACE)
class Image(Container):
    # TODO: Implement this
    pass


@register_class('SpecFile', CORE_NAMESPACE)
class SpecFile(Container):
    # TODO: Implement this
    pass


@register_class('NWBFile', CORE_NAMESPACE)
class NWBFile(NWBContainer):
    """
    A representation of an NWB file.
    """
    __nwbfields__ = ('experimenter',
                     'description',
                     'experiment_description',
                     'session_id',
                     'lab',
                     'institution',
                     'acquisition',
                     'stimulus',
                     'stimulus_template',
                     'ec_electrodes',
                     'ec_electrode_groups',
                     'ic_electrodes',
                     'imaging_planes',
                     'optogenetic_sites',
                     'modules',
                     'epochs',
                     'epoch_tags',
                     'devices')

    __current_version = None

    @classmethod
    def set_version(cls, version):
        if cls.__current_version is not None:
            msg = 'version already set'
            raise ValueError(msg)
        cls.__current_version = version

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'session_description', 'type': str,
             'doc': 'a description of the session where this data was generated'},
            {'name': 'identifier', 'type': str, 'doc': 'a unique text identifier for the file'},
            {'name': 'session_start_time', 'type': (datetime, str), 'doc': 'the start time of the recording session'},
            {'name': 'file_create_date', 'type': (list, datetime, str),
             'doc': 'the time the file was created and subsequenct modifications made', 'default': None},
            {'name': 'version', 'type': str, 'doc': 'the NWB version', 'default': None},
            {'name': 'experimenter', 'type': str, 'doc': 'name of person who performed experiment', 'default': None},
            {'name': 'experiment_description', 'type': str,
             'doc': 'general description of the experiment', 'default': None},
            {'name': 'session_id', 'type': str, 'doc': 'lab-specific ID for the session', 'default': None},
            {'name': 'institution', 'type': str,
             'doc': 'institution(s) where experiment is performed', 'default': None},
            {'name': 'lab', 'type': str, 'doc': 'lab where experiment was performed', 'default': None},
            {'name': 'acquisition', 'type': (list, tuple),
             'doc': 'Raw TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus', 'type': (list, tuple),
             'doc': 'Stimulus TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus_template', 'type': (list, tuple),
             'doc': 'Stimulus template TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'epochs', 'type': (list, tuple),
             'doc': 'Epoch objects belonging to this NWBFile', 'default': None},
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
            {'name': 'optogenetic_sites', 'type': (list, tuple),
             'doc': 'OptogeneticStimulusSites that belong to this NWBFile', 'default': None},
            {'name': 'devices', 'type': (list, tuple),
             'doc': 'Device objects belonging to this NWBFile', 'default': None})
    def __init__(self, **kwargs):
        pargs, pkwargs = fmt_docval_args(super(NWBFile, self).__init__, kwargs)
        pkwargs['name'] = 'root'
        super(NWBFile, self).__init__(*pargs, **pkwargs)
        self.__start_time = datetime.utcnow()
        # set version
        version = getargs('version', kwargs)
        if version is None:
            version = self.__current_version
        self.__nwb_version = version
        self.__session_description = getargs('session_description', kwargs)
        self.__identifier = getargs('identifier', kwargs)
        self.__session_start_time = getargs('session_start_time', kwargs)
        if isinstance(self.__session_start_time, str):
            self.__session_start_time = parse_date(self.__session_start_time)
        self.__file_create_date = getargs('file_create_date', kwargs)
        if self.__file_create_date is None:
            self.__file_create_date = datetime.now()
        if isinstance(self.__file_create_date, datetime):
            self.__file_create_date = [self.__file_create_date]
        elif isinstance(self.__file_create_date, str):
            self.__file_create_date = [parse_date(self.__file_create_date)]

        self.__acquisition = self.__build_ts(getargs('acquisition', kwargs))
        self.__stimulus = self.__build_ts(getargs('stimulus', kwargs))
        self.__stimulus_template = self.__build_ts(getargs('stimulus_template', kwargs))

        self.__modules = self.__to_dict(getargs('modules', kwargs))
        self.__epochs = self.__to_dict(getargs('epochs', kwargs))
        self.__ec_electrodes = getargs('ec_electrodes', kwargs)
        self.__ec_electrode_groups = self.__to_dict(getargs('ec_electrode_groups', kwargs))
        self.__devices = self.__to_dict(getargs('devices', kwargs))

        self.__ic_electrodes = self.__to_dict(getargs('ic_electrodes', kwargs))

        self.__imaging_planes = self.__to_dict(getargs('imaging_planes', kwargs))

        recommended = [
            'experimenter',
            'experiment_description',
            'session_id',
            'lab',
            'institution'
        ]
        for attr in recommended:
            setattr(self, attr, kwargs.get(attr, None))

    def __to_dict(self, arg):
        if arg is None:
            return dict()
        else:
            return {i.name: i for i in arg}

    def __build_ts(self, const_arg):
        ret = dict()
        if const_arg:
            for ts in const_arg:
                self.__set_timeseries(ret, ts)
        return ret

    @property
    def devices(self):
        return self.__devices

    @property
    def epochs(self):
        return self.__epochs

    @property
    def epoch_tags(self):
        ret = set()
        for epoch_name, epoch_obj in self.__epochs.items():
            ret.update(epoch_obj.tags)
        return sorted(ret)

    @property
    def modules(self):
        return self.__modules

    @property
    def identifier(self):
        return self.__identifier

    @property
    def nwb_version(self):
        return self.__nwb_version

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
    def acquisition(self):
        return tuple(self.__acquisition.values())

    @property
    def stimulus(self):
        return tuple(self.__stimulus.values())

    @property
    def stimulus_template(self):
        return tuple(self.__stimulus_template.values())

    @property
    def ec_electrodes(self):
        return self.__ec_electrodes

    @docval(*get_docval(ElectrodeTable.add_row))
    def add_electrode(self, **kwargs):
        if self.__ec_electrodes is None:
            self.__ec_electrodes = ElectrodeTable('electrodes')
        call_docval_func(self.__ec_electrodes.add_row, kwargs)

    @property
    def ec_electrode_groups(self):
        return tuple(self.__ec_electrode_groups.values())

    @property
    def ic_electrodes(self):
        return tuple(self.__ic_electrodes.values())

    @property
    def imaging_planes(self):
        return tuple(self.__imaging_planes.values())

    @docval(*filter(_not_parent, get_docval(ImagingPlane.__init__)),
            returns='the imaging plane', rtype=ImagingPlane)
    def create_imaging_plane(self, **kwargs):
        """
        Add metadata about an imaging plane
        """
        ip_args, ip_kwargs = fmt_docval_args(ImagingPlane.__init__, kwargs)
        img_pln = ImagingPlane(*ip_args, **ip_kwargs)
        self.set_imaging_plane(img_pln)
        return img_pln

    @docval({'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'the ImagingPlane object to add to this NWBFile'})
    def set_imaging_plane(self, **kwargs):
        """
        Add an ImagingPlane object to this file
        """
        img_pln = getargs('imaging_plane', kwargs)
        img_pln.parent = self
        name = img_pln.name
        self.__imaging_planes[name] = img_pln

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the imaging plane'})
    def get_imaging_plane(self, **kwargs):
        """
        Get an ImagingPlane object from this file
        """
        name = getargs('name', kwargs)
        return self.__imaging_planes.get(name)

    def is_acquisition(self, ts):
        return self.__exists(ts, self.__acquisition)

    def is_stimulus(self, ts):
        return self.__exists(ts, self.__stimulus)

    def is_stimulus_template(self, ts):
        return self.__exists(ts, self.__stimulus_template)

    def __exists(self, ts, d):
        return ts.name in d

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the epoch, as it will appear in the file'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'start', 'type': float, 'doc': 'the starting time of the epoch'},
            {'name': 'stop', 'type': float, 'doc': 'the ending time of the epoch'},
            {'name': 'tags', 'type': (tuple, list), 'doc': 'tags for this epoch', 'default': list()},
            {'name': 'description', 'type': str, 'doc': 'a description of this epoch', 'default': None})
    def create_epoch(self, **kwargs):
        """
        Creates a new Epoch object. Epochs are used to track intervals
        in an experiment, such as exposure to a certain type of stimuli
        (an interval where orientation gratings are shown, or of
        sparse noise) or a different paradigm (a rat exploring an
        enclosure versus sleeping between explorations)
        """
        ep_args, ep_kwargs = fmt_docval_args(Epoch.__init__, kwargs)
        epoch = Epoch(*ep_args, **ep_kwargs)
        self.__epochs[epoch.name] = epoch
        return epoch

    def get_epoch(self, name):
        return self.__get_epoch(name)

    @docval({'name': 'epoch', 'type': (str, Epoch, list, tuple),
             'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects'},
            {'name': 'timeseries', 'type': (str, TimeSeries, list, tuple),
             'doc': 'the name of a timeseries or a TimeSeries object or a list of \
             names of timeseries or TimeSeries objects'})
    def set_epoch_timeseries(self, **kwargs):
        """
        Add one or more TimSeries datasets to one or more Epochs
        """
        epoch, timeseries = getargs('epoch', 'timeseries', kwargs)
        if isinstance(epoch, list):
            ep_objs = [self.__get_epoch(ep) for ep in epoch]
        else:
            ep_objs = [self.__get_epoch(epoch)]

        if isinstance(timeseries, list):
            ts_objs = [self.__get_timeseries_obj(ts) for ts in timeseries]
        else:
            ts_objs = [self.__get_timeseries_obj(timeseries)]

        for ep in ep_objs:
            for ts in ts_objs:
                ep.add_timeseries(ts)

    def __get_epoch(self, epoch):
        if isinstance(epoch, Epoch):
            ep = epoch
        elif isinstance(epoch, str):
            ep = self.__epochs.get(epoch)
            if not ep:
                raise KeyError("Epoch '%s' not found" % epoch)
        else:
            raise TypeError(type(epoch))
        return ep

    def __get_timeseries_obj(self, timeseries):
        if isinstance(timeseries, TimeSeries):
            ts = timeseries
        elif isinstance(timeseries, str):
            ts = self.__acquisition.get(timeseries,
                                        self.__stimulus.get(timeseries,
                                                            self.__stimulus_template.get(timeseries, None)))
            if not ts:
                raise KeyError("TimeSeries '%s' not found" % timeseries)
        else:
            raise TypeError(type(timeseries))
        return ts

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch, list, tuple), 'doc': 'the name of an epoch \
            or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_acquisition(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__acquisition, ts, epoch)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this TimeSeries'})
    def get_acquisition(self, **kwargs):
        '''
        Retrieve acquisition TimeSeries data
        '''
        name = getargs('name', kwargs)
        return self.__get_timeseries(self.__acquisition, name)

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch),
             'doc': 'the name of an epoch or an Epoch object or a list of names of \
             epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__stimulus, ts, epoch)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this TimeSeries'})
    def get_stimulus(self, **kwargs):
        '''
        Retrieve stimiulus TimeSeries data
        '''
        name = getargs('name', kwargs)
        return self.__get_timeseries(self.__stimulus, name)

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch),
             'doc': 'the name of an epoch or an Epoch object or a list of names of \
             epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus_template(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__stimulus_template, ts, epoch)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this TimeSeries'})
    def get_stimulus_template(self, **kwargs):
        '''
        Retrieve stimiulus template TimeSeries data
        '''
        name = getargs('name', kwargs)
        return self.__get_timeseries(self.__stimulus_template, name)

    def __set_timeseries(self, ts_dict, ts, epoch=None):
        ts_dict[ts.name] = ts
        if ts.parent is None:
            ts.parent = self
        if epoch:
            self.set_epoch_timeseries(epoch, ts)

    def __get_timeseries(self, ts_dict, name):
        ret = ts_dict.get(name)
        if ret is None:
            msg = "no TimeSeries named '%s' found" % name
            raise ValueError(msg)
        return ret

    @docval(*filter(_not_parent, get_docval(ElectrodeGroup.__init__)),
            returns='the electrode group', rtype=ElectrodeGroup)
    def create_electrode_group(self, **kwargs):
        """
        Add an electrode group (e.g. a probe, shank, tetrode).
        """
        eg_args, eg_kwargs = fmt_docval_args(ElectrodeGroup.__init__, kwargs)
        elec_grp = ElectrodeGroup(*eg_args, **eg_kwargs)
        self.set_electrode_group(elec_grp)
        return elec_grp

    @docval({'name': 'electrode_grp', 'type': ElectrodeGroup,
             'doc': 'the ElectrodeGroup object to add to this NWBFile'})
    def set_electrode_group(self, **kwargs):
        elec_grp = getargs('electrode_grp', kwargs)
        elec_grp.parent = self
        name = elec_grp.name
        self.__ec_electrode_groups[name] = elec_grp

    @docval({'name': 'electrode_table', 'type': ElectrodeTable, 'doc': 'the ElectrodeTable for this file'})
    def set_electrode_table(self, **kwargs):
        if self.__ec_electrodes is not None:
            msg = 'ElectrodeTable already exists, cannot overwrite'
            raise ValueError(msg)
        electrode_table = getargs('electrode_table', kwargs)
        self.__ec_electrodes = electrode_table

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this device'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            returns='the recording device', rtype=Device)
    def create_device(self, **kwargs):
        name, source = getargs('name', 'source', kwargs)
        device = Device(name=name, source=source)
        self.set_device(device)  # This also sets the parent of the device
        return device

    @docval({'name': 'device', 'type': Device, 'doc': 'the Device object to add to this NWBFile'})
    def set_device(self, **kwargs):
        device = getargs('device', kwargs)
        device.parent = self
        name = device.name
        self.__devices[name] = device

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the electrode group'})
    def get_electrode_group(self, **kwargs):
        name = getargs('name', kwargs)
        return self.__ec_electrode_groups.get(name)

    @docval(*filter(_not_parent, get_docval(IntracellularElectrode.__init__)),
            returns='the intracellular electrode', rtype=IntracellularElectrode)
    def create_intracellular_electrode(self, **kwargs):
        ie_args, ie_kwargs = fmt_docval_args(IntracellularElectrode.__init__, kwargs)
        ic_elec = IntracellularElectrode(*ie_args, **ie_kwargs)
        self.set_intracellular_electrode(ic_elec)
        return ic_elec

    @docval({'name': 'ic_elec', 'type': IntracellularElectrode,
             'doc': 'the IntracellularElectrode object to add to this NWBFile'})
    def set_intracellular_electrode(self, **kwargs):
        ic_elec = getargs('ic_elec', kwargs)
        ic_elec.parent = self
        name = ic_elec.name
        self.__ic_electrodes[name] = ic_elec

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the intracellular electrode'})
    def get_intracellular_electrode(self, **kwargs):
        '''
        Retrieve an IntracellularElectrode
        '''
        name = getargs('name', kwargs)
        return self.__ic_electrodes.get(name)

    @docval({'name': 'name',  'type': str, 'doc': 'the name of the processing module'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description',  'type': str, 'doc': 'description of the processing module'},
            returns="a processing module", rtype=ProcessingModule)
    def create_processing_module(self, **kwargs):
        '''
        Creates a ProcessingModule object of the specified name. NWBContainers can
        be created by the module and will be stored inside it
        '''
        cargs, ckwargs = fmt_docval_args(ProcessingModule.__init__, kwargs)
        ret = ProcessingModule(*cargs, **ckwargs)
        self.set_processing_module(ret)
        return ret

    @docval({'name': 'module',  'type': ProcessingModule, 'doc': 'the processing module to add to this file'})
    def set_processing_module(self, **kwargs):
        '''
        Add a ProcessingModule to this NWBFile
        '''
        module = getargs('module', kwargs)
        if module.parent is None:
            module.parent = self
        self.__modules[module.name] = module

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the processing module'})
    def get_processing_module(self, **kwargs):
        '''
        Retrieve a ProcessingModule
        '''
        name = getargs('name', kwargs)
        return self.__modules.get(name)
