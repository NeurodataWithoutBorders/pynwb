import warnings
from collections.abc import Iterable
from bisect import bisect_left, bisect_right

import numpy as np

from hdmf.utils import docval, getargs, popargs, popargs_to_dict, get_docval

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .ecephys import ElectrodeGroup
from hdmf.common import DynamicTable, DynamicTableRegion


@register_class('AnnotationSeries', CORE_NAMESPACE)
class AnnotationSeries(TimeSeries):
    """Stores text-based records about the experiment.
    To use the AnnotationSeries, add records individually through add_annotation(). Alternatively, if all annotations
    are already stored in a list or numpy array, set the data and timestamps in the constructor.
    """

    __nwbfields__ = ()

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': 'The annotations over time. Must be 1D.',
             'default': list()},
            *get_docval(TimeSeries.__init__, 'timestamps', 'comments', 'description'))
    def __init__(self, **kwargs):
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        super().__init__(name=name, data=data, unit='n/a', resolution=-1.0, timestamps=timestamps, **kwargs)

    @docval({'name': 'time', 'type': float, 'doc': 'The time for the annotation'},
            {'name': 'annotation', 'type': str, 'doc': 'the annotation'})
    def add_annotation(self, **kwargs):
        """Add an annotation."""
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

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'feature_units', 'type': Iterable, 'shape': (None, ),  # required
             'doc': 'The unit of each feature'},
            {'name': 'features', 'type': Iterable, 'shape': (None, ),  # required
             'doc': 'Description of each feature'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ((None,), (None, None)),
             'doc': ('The data values. May be 1D or 2D. The first dimension must be time. The optional second '
                     'dimension represents features'),
             'default': list()},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'offset'))
    def __init__(self, **kwargs):
        name, data, features, feature_units = popargs('name', 'data',
                                                              'features', 'feature_units', kwargs)
        super().__init__(name=name, data=data, unit="see 'feature_units'", **kwargs)
        self.features = features
        self.feature_units = feature_units

    @docval({'name': 'time', 'type': float, 'doc': 'the time point of this feature'},
            {'name': 'features', 'type': (list, np.ndarray), 'doc': 'the feature values for this time point'})
    def add_features(self, **kwargs):
        time, features = getargs('time', 'features', kwargs)
        if isinstance(self.timestamps, list) and isinstance(self.data, list):
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

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': ('The data values. Must be 1D, where the first dimension must be time. Values are >0 if '
                     'interval started, <0 if interval ended.'),
             'default': list()},
            *get_docval(TimeSeries.__init__, 'timestamps', 'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        self.__interval_timestamps = timestamps
        self.__interval_data = data
        super().__init__(name=name, data=data, unit='n/a', resolution=-1.0, timestamps=timestamps, **kwargs)

    @docval({'name': 'start', 'type': float, 'doc': 'The start time of the interval'},
            {'name': 'stop', 'type': float, 'doc': 'The stop time of the interval'})
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

    __fields__ = (
        'waveform_rate',
        'waveform_unit',
        'resolution'
    )

    waveforms_desc = ('Individual waveforms for each spike. If the dataset is three-dimensional, the third dimension '
                      'shows the response from different electrodes that all observe this unit simultaneously. In this'
                      ' case, the `electrodes` column of this Units table should be used to indicate which electrodes '
                      'are associated with this unit, and the electrodes dimension here should be in the same order as'
                      ' the electrodes referenced in the `electrodes` column of this table.')
    __columns__ = (
        {'name': 'spike_times', 'description': 'the spike times for each unit', 'index': True},
        {'name': 'obs_intervals', 'description': 'the observation intervals for each unit',
         'index': True},
        {'name': 'electrodes', 'description': 'the electrodes that each spike unit came from',
         'index': True, 'table': True},
        {'name': 'electrode_group', 'description': 'the electrode group that each spike unit came from'},
        {'name': 'waveform_mean', 'description': 'the spike waveform mean for each spike unit'},
        {'name': 'waveform_sd', 'description': 'the spike waveform standard deviation for each spike unit'},
        {'name': 'waveforms', 'description': waveforms_desc, 'index': 2}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'Name of this Units interface', 'default': 'Units'},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'),
            {'name': 'description', 'type': str, 'doc': 'a description of what is in this table', 'default': None},
            {'name': 'electrode_table', 'type': DynamicTable,
             'doc': 'the table that the *electrodes* column indexes', 'default': None},
            {'name': 'waveform_rate', 'type': float,
             'doc': 'Sampling rate of the waveform means', 'default': None},
            {'name': 'waveform_unit', 'type': str,
             'doc': 'Unit of measurement of the waveform means', 'default': 'volts'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest possible difference between two spike times', 'default': None}
            )
    def __init__(self, **kwargs):
        args_to_set = popargs_to_dict(("waveform_rate", "waveform_unit", "resolution"), kwargs)
        electrode_table = popargs("electrode_table", kwargs)
        if kwargs['description'] is None:
            kwargs['description'] = "data on spiking units"
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

        if 'spike_times' not in self.colnames:
            self.__has_spike_times = False
        self.__electrode_table = electrode_table

    @docval({'name': 'spike_times', 'type': 'array_data', 'doc': 'the spike times for each unit',
             'default': None, 'shape': (None,)},
            {'name': 'obs_intervals', 'type': 'array_data',
             'doc': 'the observation intervals (valid times) for each unit. All spike_times for a given unit ' +
             'should fall within these intervals. [[start1, end1], [start2, end2], ...]',
             'default': None, 'shape': (None, 2)},
            {'name': 'electrodes', 'type': 'array_data', 'doc': 'the electrodes that each unit came from',
             'default': None},
            {'name': 'electrode_group', 'type': ElectrodeGroup, 'default': None,
             'doc': 'the electrode group that each unit came from'},
            {'name': 'waveform_mean', 'type': 'array_data',
             'doc': 'the spike waveform mean for each unit. Shape is (time,) or (time, electrodes)',
             'default': None},
            {'name': 'waveform_sd', 'type': 'array_data', 'default': None,
             'doc': 'the spike waveform standard deviation for each unit. Shape is (time,) or (time, electrodes)'},
            {'name': 'waveforms', 'type': 'array_data', 'default': None, 'doc': waveforms_desc,
             'shape': ((None, None), (None, None, None))},
            {'name': 'id', 'type': int, 'default': None, 'doc': 'the id for each unit'},
            allow_extra=True)
    def add_unit(self, **kwargs):
        """
        Add a unit to this table
        """
        super().add_row(**kwargs)
        if 'electrodes' in self:
            elec_col = self['electrodes'].target
            if elec_col.table is None:
                if self.__electrode_table is None:
                    nwbfile = self.get_ancestor(data_type='NWBFile')
                    elec_col.table = nwbfile.electrodes
                    if elec_col.table is None:
                        warnings.warn('Reference to electrode table that does not yet exist')
                else:
                    elec_col.table = self.__electrode_table

    @docval({'name': 'index', 'type': (int, list, tuple, np.ndarray),
             'doc': 'the index of the unit in unit_ids to retrieve spike times for'},
            {'name': 'in_interval', 'type': (tuple, list), 'doc': 'only return values within this interval',
             'default': None, 'shape': (2,)})
    def get_unit_spike_times(self, **kwargs):
        index, in_interval = getargs('index', 'in_interval', kwargs)
        if type(index) in (list, tuple):
            return [self.get_unit_spike_times(i, in_interval=in_interval) for i in index]
        if in_interval is None:
            return np.asarray(self['spike_times'][index])
        else:
            st = self['spike_times']
            unit_start = 0 if index == 0 else st.data[index - 1]
            unit_stop = st.data[index]
            start_time, stop_time = in_interval

            ind_start = bisect_left(st.target, start_time, unit_start, unit_stop)
            ind_stop = bisect_right(st.target, stop_time, ind_start, unit_stop)

            return np.asarray(st.target[ind_start:ind_stop])

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the unit in unit_ids to retrieve observation intervals for'})
    def get_unit_obs_intervals(self, **kwargs):
        index = getargs('index', kwargs)
        return np.asarray(self['obs_intervals'][index])


@register_class('DecompositionSeries', CORE_NAMESPACE)
class DecompositionSeries(TimeSeries):
    """
    Stores product of spectral analysis
    """

    __nwbfields__ = ('metric',
                     {'name': 'source_timeseries', 'child': False, 'doc': 'the input TimeSeries from this analysis'},
                     {'name': 'source_channels', 'child': True, 'doc': 'the channels that provided the source data'},
                     {'name': 'bands',
                      'doc': 'the bands that the signal is decomposed into', 'child': True})

    # value used when a DecompositionSeries is read and missing data
    DEFAULT_DATA = np.ndarray(shape=(0, 0, 0), dtype=np.uint8)

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),  # required
             'doc': ('The data values. Must be 3D, where the first dimension must be time, the second dimension must '
                     'be channels, and the third dimension must be bands.'),
             'shape': (None, None, None)},
            *get_docval(TimeSeries.__init__, 'description'),
            {'name': 'metric', 'type': str,  # required
             'doc': "metric of analysis. recommended - 'phase', 'amplitude', 'power'"},
            {'name': 'unit', 'type': str, 'doc': 'SI unit of measurement', 'default': 'no unit'},
            {'name': 'bands', 'type': DynamicTable,
             'doc': 'a table for describing the frequency bands that the signal was decomposed into', 'default': None},
            {'name': 'source_timeseries', 'type': TimeSeries,
             'doc': 'the input TimeSeries from this analysis', 'default': None},
            {'name': 'source_channels', 'type': DynamicTableRegion,
             'doc': ('The channels that provided the source data. In the case of electrical recordings this is '
                     'typically a DynamicTableRegion pointing to the electrodes table at NWBFile.electrodes, '
                     'similar to ElectricalSeries.electrodes.'),
             'default': None},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'control', 'control_description', 'offset'))
    def __init__(self, **kwargs):
        metric, source_timeseries, bands, source_channels = popargs('metric', 'source_timeseries', 'bands',
                                                                    'source_channels', kwargs)
        super().__init__(**kwargs)
        self.source_timeseries = source_timeseries
        self.source_channels = source_channels
        if self.source_timeseries is None and self.source_channels is None:
            warnings.warn("Neither source_timeseries nor source_channels is present in DecompositionSeries. It is "
                          "recommended to indicate the source timeseries if it is present, or else to link to the "
                          "corresponding source_channels. (Optional)")
        self.metric = metric
        if bands is None:
            bands = DynamicTable(
                name="bands",
                description="data about the frequency bands that the signal was decomposed into"
            )
        self.bands = bands

    def __check_column(self, name, desc):
        if name not in self.bands.colnames:
            self.bands.add_column(name, desc)

    @docval({'name': 'band_name', 'type': str, 'doc': 'the name of the frequency band',
             'default': None},
            {'name': 'band_limits', 'type': ('array_data', 'data'), 'default': None,
             'doc': 'low and high frequencies of bandpass filter in Hz'},
            {'name': 'band_mean', 'type': float, 'doc': 'the mean of Gaussian filters in Hz',
             'default': None},
            {'name': 'band_stdev', 'type': float, 'doc': 'the standard deviation of Gaussian filters in Hz',
             'default': None},
            allow_extra=True)
    def add_band(self, **kwargs):
        """
        Add ROI data to this
        """
        band_name, band_limits, band_mean, band_stdev = getargs('band_name', 'band_limits', 'band_mean', 'band_stdev',
                                                                kwargs)
        if band_name is not None:
            self.__check_column('band_name', "the name of the frequency band (recommended: 'alpha', 'beta', 'gamma', "
                                             "'delta', 'high gamma'")
        if band_name is not None:
            self.__check_column('band_limits', 'low and high frequencies of bandpass filter in Hz')
        if band_mean is not None:
            self.__check_column('band_mean', 'the mean of Gaussian filters in Hz')
        if band_stdev is not None:
            self.__check_column('band_stdev', 'the standard deviation of Gaussian filters in Hz')

        self.bands.add_row({k: v for k, v in kwargs.items() if v is not None})
