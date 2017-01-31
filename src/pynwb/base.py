# Copyright (c) 2015 Allen Institute, California Institute of Technology, 
# New York University School of Medicine, the Howard Hughes Medical 
# Institute, University of California, Berkeley, GE, the Kavli Foundation 
# and the International Neuroinformatics Coordinating Facility. 
# All rights reserved.
#     
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following 
# conditions are met:
#     
# 1.  Redistributions of source code must retain the above copyright 
#     notice, this list of conditions and the following disclaimer.
#     
# 2.  Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in 
#     the documentation and/or other materials provided with the distribution.
#     
# 3.  Neither the name of the copyright holder nor the names of its 
#     contributors may be used to endorse or promote products derived 
#     from this software without specific prior written permission.
#     
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
import numpy as np
from collections import Iterable

from pynwb.core import docval, getargs, popargs, NWBContainer

_default_conversion = 1.0
_default_resolution = np.nan

class TimeSeries(NWBContainer):
    """ Standard TimeSeries constructor

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    """
        # if modality == "acquisition":
        #     self.path = "/acquisition/timeseries/"
        # elif modality == "stimulus":
        #     self.path = "/stimulus/presentation/"
        # elif modality == "template":
        #     self.path = "/stimulus/templates/"
    __nwbfields__ = ("name",
                     "comments",
                     "description",
                     "source",
                     "data",
                     "resolution",
                     "conversion",
                     "unit",
                     "num_samples",
                     "timestamps",
                     "timestamps_unit",
                     "interval",
                     "starting_time",
                     "rate",
                     "rate_unit",
                     "control",
                     "control_description",
                     "ancestry",
                     "neurodata_type",
                     "help")

    __ancestry = 'TimeSeries'
    __neurodata_type = 'TimeSeries'
    __help = 'General purpose TimeSeries'

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, 'TimeSeries'), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},

            ## time related data is optional, but one is required -- this will have to be enforced in the constructor
            {'name': 'timestamps', 'type': (list, np.ndarray, 'TimeSeries'), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """
        super(TimeSeries, self).__init__(parent=kwargs.get('parent'))
        keys = ("name",
                "source",
                "comments",
                "description",
                "resolution",
                "conversion",
                "unit",
                "control",
                "control_description")
        for key in keys:
            setattr(self, key, kwargs.get(key))

        data = getargs('data', kwargs)
        self.fields['data'] = data
        if isinstance(data, TimeSeries):
            data.fields['data_link'].add(self)

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None: 
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = 'Seconds'
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.fields['timestamps_link'].add(self)
        elif starting_time is not None and rate is not None:
            self.starting_time = starting_time
            self.rate = rate
            self.rate_unit = 'Seconds'
        else:
            raise TypeError("either 'timestamps' or 'starting_time' and 'rate' must be specified") from None

        self.fields['data_link'] = set()
        self.fields['timestamps_link'] = set()

    @property
    def ancestry(self):
        return self.__ancestry

    @property
    def neurodata_type(self):
        return self.__neurodata_type

    @property
    def help(self):
        return self.__help

    @property
    def data(self):
        if isinstance(self.fields['data'], TimeSeries):
            return self.fields['data'].data
        else:
            return self.fields['data']

    @property
    def data_link(self):
        return frozenset(self.fields['data_link'])

    @property
    def timestamps(self):
        if isinstance(self.fields['timestamps'], TimeSeries):
            return self.fields['timestamps'].timestamps
        else:
            return self.fields['timestamps']

    @property
    def timestamps_link(self):
        return frozenset(self.fields['timestamps_link'])

    @property
    def time_unit(self):
        return self.__time_unit


    # have special calls for those that are common to all time series
    
    @docval({'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset'})
    def set_description(self, **kwargs):
        """ Convenience function to set the description field of the
            *TimeSeries*
        """
        self.description = kwargs['description']

    @docval({'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset'})
    def set_comments(self, **kwargs):
        """ Convenience function to set the comments field of the
            *TimeSeries*
        """
        self.comments = kwargs['comments']


class Module(NWBContainer):
    """ Processing module. This is a container for one or more interfaces
        that provide data at intermediate levels of analysis

        Modules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """
    def __init__(self, name, nwb, spec):
        self.name = name
        self.nwb = nwb
        self.spec = copy.deepcopy(spec)
        # a place to store interfaces belonging to this module
        self.ifaces = {}
        # create module folder immediately, so it's available 
        folder = self.nwb.file_pointer["processing"]
        if name in folder:
            nwb.fatal_error("Module '%s' already exists" % name)
        self.mod_folder = folder.create_group(self.name)
        self.serial_num = -1
        # 
        self.finalized = False

    def full_path(self):
        """ Returns HDF5 path of module

            Arguments:
                *none*

            Returns:
                (text) the HDF5 path to the module
        """
        return "processing/" + self.name

    def __build_electrical_ts(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = _timeseries.ElectricalSeries(name, electrodes=electrode_indices)
        ts.set_data(data)
        if timestamps:
            ts.set_timestamps(timestamps)
        elif start_rate:
            ts.set_time_by_rate(start_rate[0], start_rate[1])
        return ts

    def add_lfp(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = self.__build_electrical_ts(data, 
                                        electrode_indices,
                                        timestamps=timestamps,
                                        start_rate=start_rate)
        iface = _ephys.LFP(lfp_ts=ts)
        return iface

    def add_filtered_ephys(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = self.__build_electrical_ts(data, 
                                        electrode_indices,
                                        timestamps=timestamps,
                                        start_rate=start_rate,
                                        name=name)
        iface = _ephys.FilteredEphys(ephys_ts=ts)
        return iface

        
#    def create_interface(self, iface_type):
#        """ Creates an interface within the module. 
#            Each module can have multiple interfaces.
#            Standard interface options are:
#
#                BehavioralEpochs -- general container for storing and
#                publishing intervals (IntervalSeries)
#
#                BehavioralEvents -- general container for storing and
#                publishing event series (TimeSeries)
#
#                BehavioralTimeSeries -- general container for storing and
#                publishing time series (TimeSeries)
#
#                Clustering -- clustered spike data, whether from
#                automatic clustering tools or as a result of manual
#                sorting
#
#                ClusterWaveform -- mean event waveform of clustered data
#
#                CompassDirection -- publishes 1+ SpatialSeries storing
#                direction in degrees (or radians) 
#
#                DfOverF -- publishes 1+ RoiResponseSeries showing
#                dF/F in observed ROIs
#
#                EventDetection -- information about detected events
#
#                EventWaveform -- publishes 1+ SpikeEventSeries
#                of extracellularly recorded spike events
#
#                EyeTracking -- publishes 1+ SpatialSeries storing 
#                direction of gaze
#
#                FeatureExtraction -- salient features of events
#
#                FilteredEphys -- publishes 1+ ElectricalSeries storing
#                data from digital filtering
#
#                Fluorescence -- publishes 1+ RoiResponseSeries showing
#                fluorescence of observed ROIs
#
#                ImageSegmentation -- publishes groups of pixels that
#                represent regions of interest in an image
#
#                LFP -- a special case of FilteredEphys, filtered and
#                downsampled for LFP signal
#
#                MotionCorrection -- publishes image stacks whos frames
#                have been corrected to account for motion
#
#                Position -- publishes 1+ SpatialSeries storing physical
#                position. This can be along x, xy or xyz axes
#
#                PupilTracking -- publishes 1+ standard *TimeSeries* 
#                that stores pupil size
#
#                UnitTimes -- published data about the time(s) spikes
#                were detected in an observed unit
#        """
#        iface_class = getattr(sys.modules[__name__], iface_type, None)
#        
#        self.interfaces[name] = iface_class(if_spec)
#
#        if iface_type not in self.nwb.spec["Interface"]:
#            self.nwb.fatal_error("unrecognized interface: " + iface_type)
#        if_spec = self.create_interface_definition(iface_type)
#        if iface_type == "ImageSegmentation":
#            iface = ImageSegmentation(iface_type, self, if_spec)
#        elif iface_type == "Clustering":
#            iface = Clustering(iface_type, self, if_spec)
#        elif iface_type == "ImagingRetinotopy":
#            iface = ImagingRetinotopy(iface_type, self, if_spec)
#        elif iface_type == "UnitTimes":
#            iface = UnitTimes(iface_type, self, if_spec)
#        elif iface_type == "MotionCorrection":
#            iface = MotionCorrection(iface_type, self, if_spec)
#        else:
#            iface = Interface(iface_type, self, if_spec)
#        self.ifaces[iface_type] = iface
#        from . import nwb as nwblib
#        iface.serial_num = nwblib.register_creation("Interface -- " + iface_type)
#        return iface
#
#    # internal function
#    # read spec to create time series definition. do it recursively 
#    #   if time series are subclassed
#    def create_interface_definition(self, if_type):
#        super_spec = copy.deepcopy(self.nwb.spec["Interface"]["SuperInterface"])
#        if_spec = self.nwb.spec["Interface"][if_type]
#        from . import nwb as nwblib
#        return nwblib.recursive_dictionary_merge(super_spec, if_spec)
#
#    def set_description(self, desc):
#        """ Set description field in module
#
#            Arguments:
#                *desc* (text) Description of module
#
#            Returns:
#                *nothing*
#        """
#        self.set_value("description", desc)
#
#    def set_value(self, key, value, **attrs):
#        """Adds a custom key-value pair (ie, dataset) to the root of 
#           the module.
#   
#           Arguments:
#               *key* (string) A unique identifier within the TimeSeries
#
#               *value* (any) The value associated with this key
#
#               *attrs* (dict) Dictionary of key-value pairs to be
#               stored as attributes
#   
#           Returns:
#               *nothing*
#        """
#        if self.finalized:
#            self.nwb.fatal_error("Added value to module after finalization")
#        self.spec[key] = copy.deepcopy(self.spec["[]"])
#        dtype = self.spec[key]["_datatype"]
#        name = "module " + self.name
#        self.nwb.set_value_internal(key, value, self.spec, name, dtype, **attrs)
#
#    def finalize(self):
#        """ Completes the module and writes changes to disk.
#
#            Arguments: 
#                *none*
#
#            Returns:
#                *nothing*
#        """
#        if self.finalized:
#            return
#        self.finalized = True
#        # finalize interfaces
#        iface_names = []
#        for k, v in self.ifaces.items():
#            v.finalize()
#            iface_names.append(v.name)
#        iface_names.sort()
#        self.spec["_attributes"]["interfaces"]["_value"] = iface_names
#        # write own data
#        grp = self.nwb.file_pointer["processing/" + self.name]
#        self.nwb.write_datasets(grp, "", self.spec)
#        from . import nwb as nwblib
#        nwblib.register_finalization(self.name, self.serial_num)

class Interface(NWBContainer):
    """ Interfaces represent particular processing tasks and they publish
        (ie, make available) specific types of data. Each is required
        to supply a minimum of specifically named data, but all can store 
        data beyond this minimum

        Interfaces should be created through Module.create_interface().
        They should not be created directly
    """
    __nwbfields__ = ("help_statement",
                     "neurodata_type",
                     "source",
                     "interface")

    _neurodata_type = "Interface"

    _interface = "Interface"

    _help_statement = None

    def __init__(self, source=None):
        #Arguments:
        #    *name* (text) name of interface (may be class name)
        #    *module* (*Module*) Reference to parent module object that 
        #       interface belongs to
        #    *spec* (dict) dictionary structure defining module specification
        #self.module = module
        #self.name = name
        #self.nwb = module.nwb
        #self.spec = copy.deepcopy(spec)
        ## timeseries that are added to interface directly
        #self.defined_timeseries = {}
        ## timeseries that exist elsewhere and are HDF5-linked
        #self.linked_timeseries = {}
        #if name in module.mod_folder:
        #    self.nwb.fatal_error("Interface %s already exists in module %s" % (name, module.name))
        #self.iface_folder = module.mod_folder.create_group(name)
        #self.serial_num = -1
        #self.finalized = False
        self._source = source
        self._timeseries = dict()

    def full_path(self):
        """ Returns HDF5 path to this interface

            Arguments:
                *none*

            Returns:
                (text) the HDF5 path to the interface
        """
        return "processing/" + self.module.name + "/" + self.name

    def create_timeseries(self, name, ts_type="TimeSeries"):
        ts_class = getattr(_timeseries, ts_type, None)
        if not ts_class:
            raise ValueError("%s is an invalid TimeSeries type" % ts_type)
        self.timeseries[name] = ts_class(name)
        return self._timeseries[name]

    def add_timeseries(self, ts, name=None):
        """ Add a previously-defined *TimeSeries* to the interface. It will
            be added as an HDF5 link

            Arguments:
                *ts_name* (text) name of time series as it will appear in
                the interface

                *path* (text) path to the time series

            Returns:
                *nothing*
        """
        if name:
            self._timeseries[name] = ts
        else:
            self._timeseries[ts.name] = ts

    def get_timeseries(self):
        return timeseries

    def set_source(self, src):
        """ Identify source(s) for the data provided in the module.
            This can be one or more other modules, or time series
            in acquisition or stimulus

            Arguments:
                *src* (text) Path to objects providing data that the
                data here is based on

            Returns:
                *nothing*
        """
        self._source = src

