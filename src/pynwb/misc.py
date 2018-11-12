import numpy as np
from collections import Iterable

from .form.utils import docval, getargs, popargs, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_conversion, _default_resolution
from .core import NWBContainer, ElementIdentifiers, DynamicTable


@register_class('AnnotationSeries', CORE_NAMESPACE)
class AnnotationSeries(TimeSeries):
    """
    Stores text-based records about the experiment. To use the
    AnnotationSeries, add records individually through
    add_annotation() and then call finalize(). Alternatively, if
    all annotations are already stored in a list, use set_data()
    and set_timestamps()
    """

    __nwbfields__ = ()

    _help = "Time-stamped annotations about an experiment."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': list()},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str, 'doc':
             'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        super(AnnotationSeries, self).__init__(name, data, 'n/a',
                                               resolution=-1.0, conversion=1.0,
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
    """

    __nwbfields__ = ('feature_units',
                     'features')

    _help = "Features of an applied stimulus. This is useful when storing the raw stimulus is impractical."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'feature_units', 'type': Iterable, 'shape': (None, ), 'doc': 'The unit of each feature'},
            {'name': 'features', 'type': Iterable, 'shape': (None, ), 'doc': 'Description of each feature'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ((None,), (None, None)),
             'default': list(),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),
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
        name, data, features, feature_units = popargs('name', 'data',
                                                              'features', 'feature_units', kwargs)
        super(AbstractFeatureSeries, self).__init__(name, data, "see 'feature_units'", **kwargs)
        self.features = features
        self.feature_units = feature_units

    @docval({'name': 'time', 'type': float, 'doc': 'the time point of this feature'},
            {'name': 'features', 'type': (list, np.ndarray), 'doc': 'the feature values for this time point'})
    def add_features(self, **kwargs):
        time, features = getargs('time', 'features', kwargs)
        if type(self.timestamps) == list and type(self.data) is list:
            self.timestamps.append(time)
            self.data.append(features)
        else:
            raise ValueError('Can only add feature if timestamps and data are lists')


@register_class('IntervalSeries', CORE_NAMESPACE)
class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The
    data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval
    types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2
    for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias
    of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable
    way.
    """

    __nwbfields__ = ()

    _help = "Stores the start and stop times for events."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': '>0 if interval started, <0 if interval ended.', 'default': list()},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
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
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        unit = 'n/a'
        self.__interval_timestamps = timestamps
        self.__interval_data = data
        super(IntervalSeries, self).__init__(name, data, unit,
                                             timestamps=timestamps,
                                             resolution=-1.0,
                                             conversion=1.0,
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


@register_class('Units', CORE_NAMESPACE)
class Units(DynamicTable):
    """
    Event times of observed units (e.g. cell, synapse, etc.).
    """

    __columns__ = (
        {'name': 'spike_times', 'description': 'the spike times for each unit', 'index': True},
        {'name': 'electrodes', 'description': 'the electrodes that each spike unit came from',
         'index': True, 'table': True},
        {'name': 'electrode_group', 'description': 'the electrode group that each spike unit came from'},
        {'name': 'waveform_mean', 'description': 'the spike waveform mean for each spike unit'},
        {'name': 'waveform_sd', 'description': 'the spike waveform standard deviation for each spike unit'}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'Name of this Units interface', 'default': 'Units'},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers),
             'doc': 'the identifiers for the units stored in this interface', 'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
             'default': None},
            {'name': 'description', 'type': str, 'doc': 'a description of what is in this table', 'default': None})
    def __init__(self, **kwargs):
        if kwargs.get('description', None) is None:
            kwargs['description'] = ""
        call_docval_func(super(Units, self).__init__, kwargs)
        if 'spike_times' not in self.colnames:
            self.__has_spike_times = False

    @docval({'name': 'spike_times', 'type': 'array_data', 'doc': 'the spike times for the unit', 'default': None},
            {'name': 'electrodes', 'type': 'array_data', 'doc': 'the electrodes that each spike unit came from',
             'default': None},
            {'name': 'electrode_group', 'type': 'array_data', 'default': None,
             'doc': 'the electrode group that each spike unit came from'},
            {'name': 'waveform_mean', 'type': 'array_data', 'doc': 'the spike waveform mean for each spike unit',
             'default': None},
            {'name': 'waveform_sd', 'type': 'array_data', 'default': None,
             'doc': 'the spike waveform standard deviation for each spike unit'},
            {'name': 'id', 'type': int, 'help': 'the ID for the ROI', 'default': None},
            allow_extra=True)
    def add_unit(self, **kwargs):
        """
        Add a unit to this table
        """
        super(Units, self).add_row(**kwargs)

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the unit in unit_ids to retrieve spike times for'})
    def get_unit_spike_times(self, **kwargs):
        index = getargs('index', kwargs)
        return np.asarray(self['spike_times'][index])
