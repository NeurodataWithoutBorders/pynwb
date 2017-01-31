from .core import docval, getargs 
from .base import TimeSeries, Interface, _default_conversion, _default_resolution

import numpy as np
from collections import Iterable


class AnnotationSeries(TimeSeries):
    ''' 
    Stores text-based records about the experiment. To use the
    AnnotationSeries, add records individually through 
    add_annotation() and then call finalize(). Alternatively, if 
    all annotations are already stored in a list, use set_data()
    and set_timestamps()

    All time series are created by calls to  NWB.create_timeseries(). 
    They should not not be instantiated directly
    ''' 

    _ancestry = "TimeSeries,AnnotationSeries"
    
    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': list()},
            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, name, modality, spec, nwb):
        name, source, data, timestamps = getargs('name', 'source', 'data', 'timestamps', kwargs)
        super(AnnotationSeries, self).__init__(name, source, data, 'n/a', resolution=np.nan, conversion=np.nan, timestamps=timestamps)


    @docval({'name': 'time', 'type': float, 'doc': 'The time for the anotation'},
            {'name': 'annotation', 'type': str, 'doc': 'the annotation'})
    def add_annotation(self, **kwargs):
        '''
        Add an annotation
        '''
        time, annotation = getargs('time', 'annotation', kwargs)
        self.fields['timestamps'].append(time)
        self.fields['data'].append(annotation)

class AbstractFeatureSeries(TimeSeries):
    """ 
    Represents the salient features of a data stream. Typically this
    will be used for things like a visual grating stimulus, where
    the bulk of data (each frame sent to the graphics card) is bulky
    and not of high value, while the salient characteristics (eg,
    orientation, spatial frequency, contrast, etc) are what important
    and are what are used for analysis

    All time series are created by calls to  NWB.create_timeseries(). 
    They should not not be instantiated directly
    """
    __nwbfields__ = ('feature_units', 'features')
    _ancestry = "TimeSeries,AbstractFeatureSeries"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'feature_units', 'type': str, 'doc': 'The unit of each feature'},
            {'name': 'features', 'type': str, 'doc': 'Description of each feature'},

            {'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames', 'default': list()},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element in data to convert it to the specified unit', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        
        name, source, data = getargs('name', 'source', 'data', kwargs)
        super(AbstractFeatureSeries, self).__init__(name, source, data, "see 'feature_units'", **kwargs)
        self.features = getargs('features', kwargs)
        self.feature_units = getargs('feature_units', kwargs)

    @docval({'name': 'time', 'type': float, 'doc': 'the time point of this feature'},
            {'name': 'features', 'type': (list, np.ndarray), 'doc': 'the feature values for this time point'})
    def add_features(self, **kwargs):
        time, features = getargs('time', 'features', kwargs)
        self.timestamps.append(time)
        self.data.append(features)

class IntervalSeries(TimeSeries):
    pass

class UnitTimes(Interface):

    iface_type = "UnitTimes"

    def __init__(self, name, module, spec):
        super(UnitTimes, self).__init__(name, module, spec)
        self.unit_list = []
    
    def add_unit(self, unit_name, unit_times, description, source):
        """ Adds data about a unit to the module, including unit name,
            description and times. 

            Arguments:
                *unit_name* (text) Name of the unit, as it will appear in the file

                *unit_times* (double array) Times that the unit spiked

                *description* (text) Information about the unit

                *source* (text) Name, path or description of where unit times originated
        """
        if unit_name not in self.iface_folder:
            self.iface_folder.create_group(unit_name)
        else:
            self.nwb.fatal_error("unit %s already exists" % unit_name)
        spec = copy.deepcopy(self.spec["<>"])
        spec["unit_description"]["_value"] = description
        spec["times"]["_value"] = unit_times
        spec["source"]["_value"] = source
        self.spec[unit_name] = spec
        #unit_times = ut.create_dataset("times", data=unit_times, dtype='f8')
        #ut.create_dataset("unit_description", data=description)
        self.unit_list.append(str(unit_name))

    def append_unit_data(self, unit_name, key, value):
        """ Add auxiliary information (key-value) about a unit.
            Data will be stored in the folder that contains data
            about that unit.

            Arguments:
                *unit_name* (text) Name of unit, as it appears in the file

                *key* (text) Key under which the data is added

                *value* (any) Data to be added

            Returns:
                *nothing*
        """
        if unit_name not in self.spec:
            self.nwb.fatal_error("unrecognized unit name " + unit_name)
        spec = copy.deepcopy(self.spec["<>"]["[]"])
        spec["_value"] = value
        self.spec[unit_name][key] = spec
        #ut.create_dataset(data_name, data=aux_data)

    def finalize(self):
        """ Extended (subclassed) finalize procedure. It creates and stores a list of all units in the module and then
            calls the superclass finalizer.

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            return
        self.spec["unit_list"]["_value"] = self.unit_list
        if len(self.unit_list) == 0:
            self.nwb.fatal_error("UnitTimes interface created with no units")
        super(UnitTimes, self).finalize()
