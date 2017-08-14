from datetime import datetime
from dateutil.parser import parse as parse_date
from collections import Iterable

from form.utils import docval, getargs, fmt_docval_args, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, ProcessingModule
from .epoch import Epoch
from .ecephys import ElectrodeGroup, Device
from .core import NWBContainer

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
                     'raw_timeseries',
                     'stimulus',
                     'stimulus_template',
                     'ec_electrodes',
                     'ic_electrodes',
                     'imaging_planes',
                     'optogenetic_sites',
                     'modules',
                     'epochs',
                     'epoch_tags',
                     'devices')

    __nwb_version = '1.0.6'

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'file_name', 'type': str, 'doc': 'path to NWB file'},
            {'name': 'session_description', 'type': str, 'doc': 'a description of the session where this data was generated'},
            {'name': 'identifier', 'type': str, 'doc': 'a unique text identifier for the file'},
            {'name': 'session_start_time', 'type': (datetime, str), 'doc': 'the start time of the recording session'},
            {'name': 'file_create_date', 'type': (list, datetime, str), 'doc': 'the time the file was created and subsequenct modifications made', 'default': None},
            {'name': 'experimenter', 'type': str, 'doc': 'name of person who performed experiment', 'default': None},
            {'name': 'experiment_description', 'type': str, 'doc': 'general description of the experiment', 'default': None},
            {'name': 'session_id', 'type': str, 'doc': 'lab-specific ID for the session', 'default': None},
            {'name': 'institution', 'type': str, 'doc': 'institution(s) where experiment is performed', 'default': None},
            {'name': 'lab', 'type': str, 'doc': 'lab where experiment was performed', 'default': None},
            {'name': 'raw_timeseries', 'type': (list, tuple), 'doc': 'Raw TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus', 'type': (list, tuple), 'doc': 'Stimulus TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'stimulus_template', 'type': (list, tuple), 'doc': 'Stimulus template TimeSeries objects belonging to this NWBFile', 'default': None},
            {'name': 'epochs', 'type': (list, tuple), 'doc': 'Epoch objects belonging to this NWBFile', 'default': None},
            {'name': 'modules', 'type': (list, tuple), 'doc': 'ProcessingModule objects belonging to this NWBFile', 'default': None},
            {'name': 'ec_electrodes', 'type': (list, tuple), 'doc': 'ElectrodeGroups that belong to this NWBFile', 'default': None},
            {'name': 'ic_electrodes', 'type': (list, tuple), 'doc': 'IntracellularElectrodes that belong to this NWBFile', 'default': None},
            {'name': 'imaging_planes', 'type': (list, tuple), 'doc': 'ImagingPlanes that belong to this NWBFile', 'default': None},
            {'name': 'optogenetic_sites', 'type': (list, tuple), 'doc': 'OptogeneticStimulusSites that belong to this NWBFile', 'default': None},
            {'name': 'devices', 'type': (list, tuple), 'doc': 'Device objects belonging to this NWBFile', 'default': None},
    )
    def __init__(self, **kwargs):
        pargs, pkwargs = fmt_docval_args(super().__init__, kwargs)
        super().__init__(*pargs, **pkwargs)
        self.__filename = getargs('file_name', kwargs)
        self.__start_time = datetime.utcnow()
        self.__file_id = '%s %s' % (self.__filename, self.__start_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
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

        self.__raw_timeseries = self.__build_ts(getargs('raw_timeseries', kwargs))
        self.__stimulus = self.__build_ts(getargs('stimulus', kwargs))
        self.__stimulus_template = self.__build_ts(getargs('stimulus_template', kwargs))

        self.__modules = self.__to_dict(getargs('modules', kwargs))
        self.__epochs = self.__to_dict(getargs('epochs', kwargs))
        self.__ec_electrodes = self.__to_dict(getargs('ec_electrodes', kwargs))
        self.__devices = self.__to_dict(getargs('devices', kwargs))

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
    def filename(self):
        return self.__filename

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
    def raw_timeseries(self):
        return tuple(self.__raw_timeseries.values())

    @property
    def stimulus(self):
        return tuple(self.__stimulus.values())

    @property
    def stimulus_template(self):
        return tuple(self.__stimulus_template.values())

    @property
    def ec_electrodes(self):
        return tuple(self.__ec_electrodes.values())

    def is_raw_timeseries(self, ts):
        return self.__exists(ts, self.__raw_timeseries)

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

    @docval({'name': 'epoch', 'type': (str, Epoch, list, tuple), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects'},
            {'name': 'timeseries', 'type': (str, TimeSeries, list, tuple), 'doc': 'the name of a timeseries or a TimeSeries object or a list of names of timeseries or TimeSeries objects'})
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
            ts_objs = [self.__get_timeseries(ts) for ts in timeseries]
        else:
            ts_objs = [self.__get_timeseries(timeseries)]

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

    def __get_timeseries(self, timeseries):
        if isinstance(timeseries, TimeSeries):
            ts = timeseries
        elif isinstance(timeseries, str):
            ts = self.__raw_timeseries.get(timeseries,
                    self.__stimulus.get(timeseries,
                        self.__stimulus_template.get(timeseries, None)))
            if not ts:
                raise KeyError("TimeSeries '%s' not found" % timeseries)
        else:
            raise TypeError(type(timeseries))
        return ts

    def link_timeseries(self, ts):
        pass

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch, list, tuple), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_raw_timeseries(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__raw_timeseries, ts, epoch)

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__stimulus, ts, epoch)

    @docval({'name': 'ts', 'type': TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus_template(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', kwargs)
        self.__set_timeseries(self.__stimulus_template, ts, epoch)

    def __set_timeseries(self, ts_dict, ts, epoch=None):
        ts_dict[ts.name] = ts
        if ts.parent is None:
            ts.parent = self
        if epoch:
            self.set_epoch_timeseries(epoch, ts)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'channel_description', 'type': Iterable, 'doc': 'array with description for each channel'},
            {'name': 'channel_location', 'type': Iterable, 'doc': 'array with location description for each channel e.g. "CA1"'},
            {'name': 'channel_filtering', 'type': Iterable, 'doc': 'array with description of filtering applied to each channel'},
            {'name': 'channel_coordinates', 'type': Iterable, 'doc': 'xyz-coordinates for each channel. use NaN for unknown dimensions'},
            {'name': 'channel_impedance', 'type': Iterable, 'doc': 'float array with impedance used on each channel. Can be 2D matrix to store a range'},
            {'name': 'description', 'type': str, 'doc': 'description of this electrode group'},
            {'name': 'location', 'type': str, 'doc': 'description of location of this electrode group'},
            {'name': 'device', 'type': Device, 'doc': 'the device that was used to record from this electrode group'},
            returns='the electrode group', rtype=ElectrodeGroup)
    def create_electrode_group(self, **kwargs):
        """Add an electrode group (e.g. a probe, shank, tetrode).
        """
        eg_args, eg_kwargs = fmt_docval_args(ElectrodeGroup.__init__, kwargs)
        elec_grp = ElectrodeGroup(*eg_args, **eg_kwargs)
        self.set_electrode_group(elec_grp)
        return elec_grp


    @docval({'name': 'elec_grp', 'type': ElectrodeGroup, 'doc': 'the ElectrodeGroup object to add to this NWBFile'})
    def set_electrode_group(self, **kwargs):
        elec_grp = getargs('elec_grp', kwargs)
        elec_grp.parent = self
        name = elec_grp.name
        self.__ec_electrodes[name] = elec_grp

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

    @docval({'name': 'name', 'type': (ElectrodeGroup, str), 'doc': 'the name of the electrode group'})
    def get_electrode_group(self, name):
        return self.__ec_electrodes.get(name)

    @docval({'name': 'name',  'type': str, 'doc': 'the name of the processing module'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description',  'type': str, 'doc': 'description of the processing module'},
            returns="a processing module", rtype=ProcessingModule)
    def create_processing_module(self, **kwargs):
        """ Creates a ProcessingModule object of the specified name. Interfaces can
            be created by the module and will be stored inside it
        """
        cargs, ckwargs = fmt_docval_args(ProcessingModule.__init__, kwargs)
        ret = ProcessingModule(*cargs, **ckwargs)
        self.add_processing_module(ret)
        return ret

    @docval({'name': 'module',  'type': ProcessingModule, 'doc': 'the processing module to add to this file'})
    def add_processing_module(self, **kwargs):
        module = getargs('module', kwargs)
        if module.parent is None:
            module.parent = self
        self.__modules[module.name] = module
