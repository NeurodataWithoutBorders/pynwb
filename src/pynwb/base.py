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
_default_resolution = float("nan")

class Interface(NWBContainer):
    """ Interfaces represent particular processing tasks and they publish
        (ie, make available) specific types of data. Each is required
        to supply a minimum of specifically named data, but all can store 
        data beyond this minimum

        Interfaces should be created through Module.create_interface().
        They should not be created directly
    """
    __nwbfields__ = ("help",
                     "neurodata_type",
                     "source")

    __neurodata_type = "Interface"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Interface'})
    def __init__(self, **kwargs):
        if self.__class__ == Interface:
            raise NotImplementedError("Interface cannot by instantiated directly")
        source = getargs('source', kwargs)
        super(Interface, self).__init__()
        self.source = source

    @property
    def name(self):
        if hasattr(self, '__name'):
            return self.__name
        else:
            return self.__class__.__name__
        return None

    @property
    def help(self):
        if hasattr(self, '__help'):
            return self.__help
        return None

class Module(NWBContainer):
    """ Processing module. This is a container for one or more interfaces
        that provide data at intermediate levels of analysis

        Modules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """

    __nwbfields__ = ('name',
                     'description',
                     'interfaces',
                     'neurodata_type')

    __neurodata_type = "Module"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'})
    def __init__(self, **kwargs):
        name, description = getargs('name', 'description', kwargs)
        super(Module, self).__init__()
        self.__name = name
        self.__interfaces = list()

    @property
    def interfaces(self):
        return tuple(self.__interfaces)

    @property
    def name(self):
        return self.__name

    @docval({'name': 'interface', 'type': Interface, 'doc': 'the Interface to add to this Module'})
    def add_interface(self, **kwargs):
        self.__interfaces.append(interface)
        interface.parent = self

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
            {'name': 'resolution', 'type': (str, float), 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': (str, float), 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},

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
