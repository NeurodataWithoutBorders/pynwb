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

from pynwb.core import docval, getargs, popargs
from ..container import NWBContainer, nwbproperties

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
                "data",
                "resolution",
                "conversion",
                "unit",
                "control",
                "control_description")
        for key in keys:
            setattr(self, key, kwargs.get(key))

        data = getargs('data', kwargs)
        self.data = data
        if isinstance(data, TimeSeries):
            data.data_link.add(self)

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None: 
            self.timestamps = timestamps
            self.timestamps_unit = 'Seconds'
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.timestamps_link.add(self)
        elif starting_time is not None and rate is not None:
            self.starting_time = starting_time
            self.rate = rate
            self.rate_unit = 'Seconds'
        else:
            raise TypeError("either 'timestamps' or 'starting_time' and 'rate' must be specified") from None
            
        self.data_link = set()
        self.timestamps_link = set()
    
    @property
    def data(self):
        if isinstance(self.fields['data'], TimeSeries):
            return self.fields['data'].data
        else:
            return self.fields['data']

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

    # if default value used, value taken from specification file
    # @docval({'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
    #         {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
    #         {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},
    #         {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution})
    # def set_data(self, **kwargs):
    #     '''
    #     Defines the data stored in the TimeSeries. Type of data 
    #     depends on which class of TimeSeries is being used
    #     '''
    #     data, unit, conversion, resolution = getargs("data", "unit", "conversion", "resolution", **kwargs)
    #     self.unit = unit
    #     self.conversion = conversion
    #     self.resolution = resolution
    #     self.data = data

    #@docval({'name': 'ts', 'type': 'TimeSeries', 'doc': 'The TimeSeries object to use the data of'})
    #def share_data(self, **kwargs):
    #    '''Links the *data* dataset in this TimeSeries to that
    #       stored in another TimeSeries. This is useful when multiple time
    #       series represent the same data.
    #    '''
    #    target_ts = kwargs['ts']
    #    while True:
    #        if isinstance(target_ts.timestamps, TimeSeries):
    #            target_ts = target_ts.timestamps
    #            continue
    #        break
    #    self.data = ts
    #    target_ts.data_link.add(self)
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

    #@docval({'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data'})
    #def set_time(self, **kwargs):
    #    ''' Store timestamps for the time series. 
    #    '''
    #    self.timestamps = kwargs['timestamps']
    #    self.interval = 1
    #    self.timestamps_unit = self.__time_unit
        
    #@docval({'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample'},
    #        {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz'})
    #def set_time_by_rate(self, **kwargs):
    #    '''Store time by start time and sampling rate only
   
    #       Arguments:
    #           *time_zero* (double) Time of data[] start. For template stimuli, this should be zero
    #           *rate* (float) Cycles per second (Hz)
   
    #       Returns:
    #           *nothing*
    #    '''
    #    starting_time, rate = getargs('starting_time', 'rate', **kwargs)
    #    self.starting_time = starting_time
    #    self.rate = rate
    #    self.starting_time_unit = self.__time_unit

    #@docval({'name': 'ts', 'type': 'TimeSeries', 'doc': 'The TimeSeries object to use the timestamps of'})
    #def share_timestamps(self, **kwargs):
    #    '''Links the *timestamps* dataset in this TimeSeries to that
    #       stored in another TimeSeries. This is useful when multiple time
    #       series have data that is recorded on the same clock.
    #       This works by making an HDF5 hard link to the timestamps array
    #       in the sibling time series
   
    #       Arguments:
    #           *sibling* (text) Full HDF5 path to TimeSeries containing source timestamps array, or a python TimeSeries object
   
    #       Returns:
    #           *nothing*
    #    '''
    #    target_ts = kwargs['ts']
    #    while True:
    #        if isinstance(target_ts.timestamps, TimeSeries):
    #            target_ts = target_ts.timestamps
    #            continue
    #        break
    #    self.timestamps = target_ts
    #    target_ts.timestamps_link.add(self)

