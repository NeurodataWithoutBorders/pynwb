import numpy as np
from collections import Iterable

from .form.utils import docval, getargs, popargs, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_conversion, _default_resolution
from .core import NWBContainer


@register_class('AnnotationSeries', CORE_NAMESPACE)
class AnnotationSeries(TimeSeries):
    """
    Stores text-based records about the experiment. To use the
    AnnotationSeries, add records individually through
    add_annotation() and then call finalize(). Alternatively, if
    all annotations are already stored in a list, use set_data()
    and set_timestamps()

    All time series are created by calls to  NWB.create_timeseries().
    They should not not be instantiated directly
    """

    __nwbfields__ = ()

    _ancestry = "TimeSeries,AnnotationSeries"
    _help = "Time-stamped annotations about an experiment."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': list()},
            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str, 'doc':
             'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, data, timestamps = popargs('name', 'source', 'data', 'timestamps', kwargs)
        super(AnnotationSeries, self).__init__(name, source, data, 'n/a',
                                               resolution=np.nan, conversion=np.nan,
                                               timestamps=timestamps, **kwargs)

    @docval({'name': 'time', 'type': float, 'doc': 'The time for the anotation'},
            {'name': 'annotation', 'type': str, 'doc': 'the annotation'})
    def add_annotation(self, **kwargs):
        '''
        Add an annotation
        '''
        time, annotation = getargs('time', 'annotation', kwargs)
        self.fields['timestamps'].append(time)
        self.fields['data'].append(annotation)


@register_class('AbstractFeatureSeries', CORE_NAMESPACE)
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

    __nwbfields__ = ('feature_units',
                     'features')

    _ancestry = "TimeSeries,AbstractFeatureSeries"
    _help = "Features of an applied stimulus. This is useful when storing the raw stimulus is impractical."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'feature_units', 'type': (str, Iterable), 'doc': 'The unit of each feature'},
            {'name': 'features', 'type': (str, Iterable), 'doc': 'Description of each feature'},

            {'name': 'data', 'type': (list, np.ndarray, Iterable, TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': list()},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},
            {'name': 'timestamps', 'type': (list, np.ndarray, Iterable, TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset',
             'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, data = popargs('name', 'source', 'data', kwargs)
        super(AbstractFeatureSeries, self).__init__(name, source, data, "see 'feature_units'", **kwargs)
        self.features = getargs('features', kwargs)
        self.feature_units = getargs('feature_units', kwargs)

    @docval({'name': 'time', 'type': float, 'doc': 'the time point of this feature'},
            {'name': 'features', 'type': (list, np.ndarray), 'doc': 'the feature values for this time point'})
    def add_features(self, **kwargs):
        time, features = getargs('time', 'features', kwargs)
        self.timestamps.append(time)
        self.data.append(features)


@register_class('IntervalSeries', CORE_NAMESPACE)
class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The
    data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval
    types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2
    for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias
    of a standard TimeSeries but that is identifiable as representing time intervals in a machinereadable
    way.
    """

    __nwbfields__ = ()

    _ancestry = "TimeSeries,IntervalSeries"
    _help = "Stores the start and stop times for events."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries, Iterable),
             'doc': '>0 if interval started, <0 if interval ended.', 'default': list()},
            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries, Iterable),
             'doc': 'Timestamps for samples stored in data', 'default': list()},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default':  'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default':  'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, data, timestamps = popargs('name', 'source', 'data', 'timestamps', kwargs)
        unit = 'n/a'
        self.__interval_timestamps = timestamps
        self.__interval_data = data
        super(IntervalSeries, self).__init__(name, source, data, unit,
                                             timestamps=timestamps,
                                             resolution=_default_resolution,
                                             conversiont=_default_conversion,
                                             **kwargs)

    @docval({'name': 'start', 'type': float, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'stop', 'type': float, 'doc': 'The name of this TimeSeries dataset'})
    def add_interval(self, **kwargs):
        start, stop = getargs('start', 'stop', kwargs)
        self.__interval_timestamps.append(start)
        self.__interval_timestamps.append(stop)
        self.__interval_data.append(1)
        self.__interval_data.append(-1)

    @property
    def data(self):
        return self.__interval_data

    @property
    def timestamps(self):
        return self.__interval_timestamps


@register_class('SpikeUnit', CORE_NAMESPACE)
class SpikeUnit(NWBContainer):
    """
    For use in the UnitTimes class.
    """

    __nwbfields__ = ('times',
                     'unit_description')

    _help = "Estimated spike times from a single unit"

    @docval({'name': 'name', 'type': str, 'doc': 'Name of the SpikeUnit'},
            {'name': 'times', 'type': Iterable, 'doc': 'Spike time for the units (exact or estimated)'},
            {'name': 'unit_description', 'type': str, 'doc': 'Description of the unit (eg, cell type).'},
            {'name': 'source', 'type': str,
             'doc': 'Name, path or description of where unit times originated. \
             This is necessary only if the info here differs from or is more fine-grained \
             than the interfaces source field.'})
    def __init__(self, **kwargs):
        times, unit_description = popargs('times', 'unit_description', kwargs)
        call_docval_func(super(SpikeUnit, self).__init__, kwargs)
        self.times = times
        self.unit_description = unit_description


@register_class('UnitTimes', CORE_NAMESPACE)
class UnitTimes(NWBContainer):
    """
    Event times of observed units (e.g. cell, synapse, etc.). The UnitTimes group contains a group
    for each unit. The name of the group should match the value in the source module, if that is
    possible/relevant (e.g., name of ROIs from Segmentation module).
    """

    __nwbfields__ = ('spike_units', 'unit_list')

    _help = "Estimated spike times from a single unit"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'spike_units', 'type': Iterable, 'doc': 'The SpikeUnits contained in this Interface'},
            {'name': 'name', 'type': str, 'doc': 'the name of this Container', 'default': 'UnitTimes'})
    def __init__(self, **kwargs):
        source, spike_units = popargs('source', 'spike_units', kwargs)
        super(UnitTimes, self).__init__(source, **kwargs)
        self.spike_units = spike_units
        # self.unit_list = [si.name for si in self.spike_units]
        # if len(self.unit_list) != len (self.spike_units):
        #    raise ValueError("Length of unit_list does not match length of spike_unit")

    @property
    def unit_list(self):
        return [si.name for si in self.spike_units]
