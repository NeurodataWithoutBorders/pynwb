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
import sys
import traceback
import copy
import numpy as np
from collections import Iterable

from ..core import docval, getargs, popargs
from .container import NWBContainer, nwbproperties

_default_conversion = 1.0
_default_resolution = np.nan

__std_fields = ("name",
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
                "control_description")
__std_static_fields = {'ancestry': 'TimeSeries',
                       'neurodata_type': 'TimeSeries',
                       'help': 'General purpose TimeSeries'}
@nwbproperties(*__std_fields, **__std_static_fields)
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

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': None},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            )
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """
        super(TimeSeries, self).__init__(parent=kwargs.get('parent'))
        keys = ("name",
                "source",
                "comments",
                "description",
                "data",
                "resolution",
                "conversion",
                "unit",
                "control",
                "control_description")
        for key in keys:
            setattr(self, key, kwargs.get(key))

        if 'timestamps' in kwargs and len(kwargs['timestamps']) > 0:
            self.timestamps = kwargs.get('timestamps')
            self.timestamps_unit = 'Seconds'
        elif 'starting_time' in kwargs and kwargs['starting_time'] is not None:
            self.starting_time = kwargs.get('starting_time')
            self.rate = kwargs.get('rate')
            self.rate_unit = self.__time_unit
            
        self.data_link = set()
        self.timestamps_link = set()
        self.interval = None
    
    @property
    def data(self):
        if isinstance(self.data, TimeSeries):
            return self.data.data
        else:
            return self.data

    @property
    def timestamps(self):
        if isinstance(self.fields['timestamps'], TimeSeries):
            return self.fields['timestamps'].timestamps
        else:
            return self.fields['timestamps']

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

    # for backward compatibility to screwy scripts, and to be nice
    #   in event of typo
    def set_comment(self, value):
        self.set_comments(value)

    # if default value used, value taken from specification file
    @docval({'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution})
    def set_data(self, **kwargs):
        '''
        Defines the data stored in the TimeSeries. Type of data 
        depends on which class of TimeSeries is being used
        '''
        data, unit, conversion, resolution = getargs("data", "unit", "conversion", "resolution", **kwargs)
        self.unit = unit
        self.conversion = conversion
        self.resolution = resolution
        self.data = data

    @docval({'name': 'ts', 'type': 'TimeSeries', 'doc': 'The TimeSeries object to use the data of'})
    def share_data(self, **kwargs):
        '''Links the *data* dataset in this TimeSeries to that
           stored in another TimeSeries. This is useful when multiple time
           series represent the same data.
        '''
        target_ts = kwargs['ts']
        while True:
            if isinstance(target_ts.timestamps, TimeSeries):
                target_ts = target_ts.timestamps
                continue
            break
        self.data = ts
        target_ts.data_link.add(self)
#
#    def ignore_data(self):
#        """ In some cases (eg, externally stored image files) there is no 
#            data to be stored. Rather than store invalid data, it's better
#            to explicitly avoid setting the data field
#
#            Arguments:
#                *none*
#
#            Returns:
#                *nothing*
#        """
#        if self.finalized:
#            self.fatal_error("Changed timeseries after finalization")
#        # downgrade required status so file will generate w/o
#        self.spec["data"]["_include"] = "standard"
#
    ####################################################################
    ####################################################################

    @docval({'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data'})
    def set_time(self, **kwargs):
        ''' Store timestamps for the time series. 
        '''
        self.timestamps = kwargs['timestamps']
        self.interval = 1
        self.timestamps_unit = self.__time_unit
        
    @docval({'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample'},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz'})
    def set_time_by_rate(self, **kwargs):
        '''Store time by start time and sampling rate only
   
           Arguments:
               *time_zero* (double) Time of data[] start. For template stimuli, this should be zero
               *rate* (float) Cycles per second (Hz)
   
           Returns:
               *nothing*
        '''
        starting_time, rate = getargs('starting_time', 'rate', **kwargs)
        self.starting_time = starting_time
        self.rate = rate
        self.starting_time_unit = self.__time_unit

    @docval({'name': 'ts', 'type': 'TimeSeries', 'doc': 'The TimeSeries object to use the timestamps of'})
    def share_timestamps(self, **kwargs):
        '''Links the *timestamps* dataset in this TimeSeries to that
           stored in another TimeSeries. This is useful when multiple time
           series have data that is recorded on the same clock.
           This works by making an HDF5 hard link to the timestamps array
           in the sibling time series
   
           Arguments:
               *sibling* (text) Full HDF5 path to TimeSeries containing source timestamps array, or a python TimeSeries object
   
           Returns:
               *nothing*
        '''
        target_ts = kwargs['ts']
        while True:
            if isinstance(target_ts.timestamps, TimeSeries):
                target_ts = target_ts.timestamps
                continue
            break
        self.timestamps = target_ts
        target_ts.timestamps_link.add(self)

class AnnotationSeries(TimeSeries):
    ''' Stores text-based records about the experiment. To use the
        AnnotationSeries, add records individually through 
        add_annotation() and then call finalize(). Alternatively, if 
        all annotations are already stored in a list, use set_data()
        and set_timestamps()

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    ''' 

    _ancestry = "TimeSeries,AnnotationSeries"
    
    def __init__(self, name, modality, spec, nwb):
        super(AnnotationSeries, self).__init__(name, modality, spec, nwb)

        self.builder.set_attribute("help", "Time-stamped annotations about an experiment")
        self.set_data(list())
        self.set_time(list())
        
        #self.annot_str = []
        #self.annot_time = []

    def add_annotation(self, what, when):
        '''Convennece function to add annotations individually

        Arguments:
            *what* (text) Annotation

            *when* (double) Timestamp for annotation

        Returns:
            *nothing*
        '''
        self.builder['data'].append(str(what))
        self.builder['timestamps'].append(str(what))

        self._data.append(str(what))
        self._timestamps.append(when)
        #self.annot_str.append(str(what))
        #self.annot_time.append(float(when))

    def set_data(self, data):
        super().set_data(data, "n/a", conversion=np.nan, resolution=np.nan)

class AbstractFeatureSeries(TimeSeries):
    """ Represents the salient features of a data stream. Typically this
        will be used for things like a visual grating stimulus, where
        the bulk of data (each frame sent to the graphics card) is bulky
        and not of high value, while the salient characteristics (eg,
        orientation, spatial frequency, contrast, etc) are what important
        and are what are used for analysis

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    """

    _ancestry = "TimeSeries,AbstractFeatureSeries"

    def set_features(self, names, units):
        """ Convenience function for setting feature values. Has logic to
            ensure arrays have equal length (ie, sanity check)

            Arguments:
                *names* (text array) Description of abstract features

                *units* (text array) Units for each of the abstract features

            Returns:
                *nothing*
        """
        self.features = names
        self.units = units
        
@nwbproperties('electrodes', ancestry='TimeSeries,ElectricalSeries')
class ElectricalSeries(TimeSeries):

    _ancestry = "TimeSeries,ElectricalSeries"
    _help = "Stores acquired voltage data from extracellular recordings"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'electrodes', 'type': (list, tuple), 'doc': 'the names of the electrode groups, or the ElectrodeGroup objects that each channel corresponds to'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': None},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            )
    def __init__(self, **kwargs):
        """ Create a new ElectricalSeries dataset
            
            Arguments:
                *names* (int array) The electrode indices
        """
        name, electrodes, source = popargs('name', 'electrodes', 'source', kwargs)
        super(ElectricalSeries, self).__init__(name, source, unit='volt', **kwargs)
        if electrodes:
            self.set_electrodes(electrodes)
    
    @docval({'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': None},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution})
    def set_data(self, **kwargs):
        """
        Set the data this ElectricalSeries contains
        """
        data, conversion, resolution = getargs('data', 'conversion', 'resolution', **kwargs)
        super().set_data(data, "volt", conversion=conversion, resolution=resolution)

    @docval({'name': 'electrodes', 'type': (list, tuple), 'doc': 'the names of the electrode groups, or the ElectrodeGroup objects that each channel corresponds to'})
    def set_electrodes(self, **kwargs):
        """ Specify the electrodes that this corresponds to in the electrode
            map.
            
            Arguments:
                *names* (int array) The electrode indices
        """
        electrodes = getargs('electrodes', **kwargs)
        self.electrodes = tuple(electrodes)


class SpikeEventSeries(ElectricalSeries):

    _ancestry = "TimeSeries,ElectricalSeries,SpikeSeries"

    _help = "Snapshots of spike events from data."

    def __init__(self, name, electrodes=None):
        super().__init__(name, electrodes)
        super().set_data(list())
        
    def add_spike_event(event_data):
        self._data.append(event_data)

class ImageSeries(TimeSeries):
    pass

class ImageMaskSeries(ImageSeries):
    pass

class OpticalSeries(ImageSeries):
    pass

class TwoPhotonSeries(ImageSeries):
    pass

class IndexSeries(TimeSeries):
    pass

class IntervalSeries(TimeSeries):
    pass

class OptogeneticSeries(TimeSeries):
    def set_data(self, data, conversion=None, resolution=None):
        super().set_data(data, "watt", conversion=conversion, resolution=resolution)

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

class RoiResponseSeries(TimeSeries):
    pass

class SpatialSeries(TimeSeries):

    _ancestry = "TimeSeries,SpatialSeries"
    
    _help = "Stores points in space over time. The data[] array structure is [num samples][num spatial dimensions]"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'reference_frame', 'type': str, 'doc': 'description defining what the zero-position is'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': None},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            )
    def __init__(self, **kwargs):
        """Create a SpatialSeries TimeSeries dataset
        """
        name, reference_frame = getargs('name', 'reference_frame', **kwargs)
        super().__init__(name)
        self.reference_frame = reference_frame

    def set_data(self, data, conversion=_default_conversion, resolution=_default_resolution):
        super().set_data(data, "meter", conversion=conversion, resolution=resolution)

