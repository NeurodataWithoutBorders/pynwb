import numpy as np
from h5py import RegionReference
from collections import Iterable

from .form.utils import docval, getargs, popargs, call_docval_func
from .form.data_utils import DataChunkIterator, ShapeValidator

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion
from .core import NWBContainer, NWBTable, NWBTableRegion, NWBDataInterface, MultiContainerInterface
from .device import Device


@register_class('ElectrodeGroup', CORE_NAMESPACE)
class ElectrodeGroup(NWBContainer):
    """
    """

    __nwbfields__ = ('name',
                     'description',
                     'location',
                     'device')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'description of this electrode group'},
            {'name': 'location', 'type': str, 'doc': 'description of location of this electrode group'},
            {'name': 'device', 'type': Device, 'doc': 'the device that was used to record from this electrode group'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ElectrodeGroup, self).__init__, kwargs)
        description, location, device = popargs("description", "location", "device", kwargs)
        self.description = description
        self.location = location
        self.device = device


_et_docval = [
    {'name': 'id', 'type': int, 'doc': 'a unique identifier for the electrode'},
    {'name': 'x', 'type': float, 'doc': 'the x coordinate of the position'},
    {'name': 'y', 'type': float, 'doc': 'the y coordinate of the position'},
    {'name': 'z', 'type': float, 'doc': 'the z coordinate of the position'},
    {'name': 'imp', 'type': float, 'doc': 'the impedance of the electrode'},
    {'name': 'location', 'type': str, 'doc': 'the location of electrode within the subject e.g. brain region'},
    {'name': 'filtering', 'type': str, 'doc': 'description of hardware filtering'},
    {'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
    {'name': 'group', 'type': ElectrodeGroup, 'doc': 'the ElectrodeGroup object to add to this NWBFile'},
    {'name': 'group_name', 'type': str, 'doc': 'the ElectrodeGroup object to add to this NWBFile', 'default': None}
]


@register_class('ElectrodeTable', CORE_NAMESPACE)
class ElectrodeTable(NWBTable):
    '''A table of all electrodes'''

    __columns__ = _et_docval

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the source of the data', 'default': list()})
    def __init__(self, **kwargs):
        data, name = getargs('data', 'name', kwargs)
        colnames = [i['name'] for i in _et_docval]
        super(ElectrodeTable, self).__init__(colnames, name, data)

    @docval(*_et_docval)
    def add_row(self, **kwargs):
        kwargs['group_name'] = kwargs['group'].name
        super(ElectrodeTable, self).add_row(kwargs)


@register_class('ElectrodeTableRegion', CORE_NAMESPACE)
class ElectrodeTableRegion(NWBTableRegion):
    '''A subsetting of an ElectrodeTable'''

    __nwbfields__ = ('description',)

    @docval({'name': 'table', 'type': ElectrodeTable, 'doc': 'the ElectrodeTable this region applies to'},
            {'name': 'region', 'type': (slice, list, tuple, RegionReference), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'electrodes'})
    def __init__(self, **kwargs):
        call_docval_func(super(ElectrodeTableRegion, self).__init__, kwargs)
        self.description = getargs('description', kwargs)


@register_class('ElectricalSeries', CORE_NAMESPACE)
class ElectricalSeries(TimeSeries):
    """
    Stores acquired voltage data from extracellular recordings. The data field of an ElectricalSeries
    is an int or float array storing data in Volts. TimeSeries::data array structure: [num times] [num
    channels] (or [num_times] for single electrode).
    """

    __nwbfields__ = ({'name': 'electrodes',
                      'doc': 'the electrodes that generated this electrical series', 'child': True},)

    __ancestry = "TimeSeries,ElectricalSeries"
    __help = "Stores acquired voltage data from extracellular recordings."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},

            {'name': 'electrodes', 'type': ElectrodeTableRegion,
             'doc': 'the table region corresponding to the electrodes from which this series was recorded'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, electrodes, data = popargs('name', 'source', 'electrodes', 'data', kwargs)
        super(ElectricalSeries, self).__init__(name, source, data, 'volt', **kwargs)
        self.electrodes = electrodes


@register_class('SpikeEventSeries', CORE_NAMESPACE)
class SpikeEventSeries(ElectricalSeries):
    """
    Stores "snapshots" of spike events (i.e., threshold crossings) in data. This may also be raw data,
    as reported by ephys hardware. If so, the TimeSeries::description field should describing how
    events were detected. All SpikeEventSeries should reside in a module (under EventWaveform
    interface) even if the spikes were reported and stored by hardware. All events span the same
    recording channels and store snapshots of equal duration. TimeSeries::data array structure:
    [num events] [num channels] [num samples] (or [num events] [num samples] for single
    electrode).
    """

    __nwbfields__ = ()

    __ancestry = "TimeSeries,ElectricalSeries,SpikeSeries"
    __help = "Snapshots of spike events from data."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data'},
            {'name': 'electrodes', 'type': ElectrodeTableRegion,
             'doc': 'the table region corresponding to the electrodes from which this series was recorded'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, data, electrodes = popargs('name', 'source', 'data', 'electrodes', kwargs)
        timestamps = getargs('timestamps', kwargs)
        if not (isinstance(data, TimeSeries) and isinstance(timestamps, TimeSeries)):
            if not (isinstance(data, DataChunkIterator) and isinstance(timestamps, DataChunkIterator)):
                if len(data) != len(timestamps):
                    raise Exception('Must provide the same number of timestamps and spike events')
            else:
                # TODO: add check when we have DataChunkIterators
                pass
        super(SpikeEventSeries, self).__init__(name, source, data, electrodes, **kwargs)


@register_class('EventDetection', CORE_NAMESPACE)
class EventDetection(NWBDataInterface):
    """
    Detected spike events from voltage trace(s).
    """

    __nwbfields__ = ('detection_method',
                     'source_electricalseries',
                     'source_idx',
                     'times')

    _help_statement = ("Description of how events were detected, such as voltage "
                       "threshold, or dV/dT threshold, as well as relevant values.")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'detection_method', 'type': str,
             'doc': 'Description of how events were detected, such as voltage threshold, or dV/dT threshold, \
             as well as relevant values.'},
            {'name': 'source_electricalseries', 'type': ElectricalSeries, 'doc': 'The source electrophysiology data'},
            {'name': 'source_idx', 'type': ('array_data', 'data'),
             'doc': 'Indices (zero-based) into source ElectricalSeries::data array corresponding \
             to time of event. Module description should define what is meant by time of event \
             (e.g., .25msec before action potential peak, zero-crossing time, etc). \
             The index points to each event from the raw data'},
            {'name': 'times', 'type': ('array_data', 'data'), 'doc': 'Timestamps of events, in Seconds'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'EventDetection'})
    def __init__(self, **kwargs):
        source, detection_method, source_electricalseries, source_idx, times = popargs(
            'source', 'detection_method', 'source_electricalseries', 'source_idx', 'times', kwargs)
        super(EventDetection, self).__init__(source, **kwargs)
        self.detection_method = detection_method
        # do not set parent, since this is a link
        self.source_electricalseries = source_electricalseries
        self.source_idx = source_idx
        self.times = times
        self.unit = 'Seconds'


@register_class('EventWaveform', CORE_NAMESPACE)
class EventWaveform(MultiContainerInterface):
    """
    Spike data for spike events detected in raw data
    stored in this NWBFile, or events detect at acquisition
    """

    __clsconf__ = {
        'attr': 'spike_event_series',
        'type': SpikeEventSeries,
        'add': 'add_spike_event_series',
        'get': 'get_spike_event_series',
        'create': 'create_spike_event_series'
    }

    __help = "Waveform of detected extracellularly recorded spike events"


@register_class('Clustering', CORE_NAMESPACE)
class Clustering(NWBDataInterface):
    """
    Specifies cluster event times and cluster metric for maximum ratio of
    waveform peak to RMS on any channel in cluster.
    """

    __nwbfields__ = (
        'description',
        'num',
        'peak_over_rms',
        'times'
    )

    __help = ("Clustered spike data, whether from automatic clustering "
              "tools (eg, klustakwik) or as a result of manual sorting.")

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data'},
            {'name': 'description', 'type': str,
             'doc': 'Description of clusters or clustering, (e.g. cluster 0 is noise, \
             clusters curated using Klusters, etc).'},
            {'name': 'num', 'type': ('array_data', 'data'), 'doc': 'Cluster number of each event.'},
            {'name': 'peak_over_rms', 'type': Iterable,
             'doc': 'Maximum ratio of waveform peak to RMS on any channel in the cluster\
             (provides a basic clustering metric).'},
            {'name': 'times', 'type': ('array_data', 'data'), 'doc': 'Times of clustered events, in seconds.'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'Clustering'})
    def __init__(self, **kwargs):
        source, description, num, peak_over_rms, times = popargs(
            'source', 'description', 'num', 'peak_over_rms', 'times', kwargs)
        super(Clustering, self).__init__(source, **kwargs)
        self.description = description
        self.num = num
        self.peak_over_rms = list(peak_over_rms)
        self.times = times


@register_class('ClusterWaveforms', CORE_NAMESPACE)
class ClusterWaveforms(NWBDataInterface):
    """
    Describe cluster waveforms by mean and standard deviation for at each sample.
    """

    __nwbfields__ = ('clustering_interface',
                     'waveform_filtering',
                     'waveform_mean',
                     'waveform_sd')

    __help = ("Mean waveform shape of clusters. Waveforms should be "
              "high-pass filtered (ie, not the same bandpass filter "
              "used waveform analysis and clustering)")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'clustering_interface', 'type': Clustering,
             'doc': 'the clustered spike data used as input for computing waveforms'},
            {'name': 'waveform_filtering', 'type': str,
             'doc': 'filter applied to data before calculating mean and standard deviation'},
            {'name': 'waveform_mean', 'type': Iterable, 'doc': 'the mean waveform for each cluster'},
            {'name': 'waveform_sd', 'type': Iterable, 'doc': 'the standard deviations of waveforms for each cluster'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'ClusterWaveforms'})
    def __init__(self, **kwargs):
        source, clustering_interface, waveform_filtering, waveform_mean, waveform_sd = popargs(
            'source', 'clustering_interface', 'waveform_filtering', 'waveform_mean', 'waveform_sd', kwargs)
        super(ClusterWaveforms, self).__init__(source, **kwargs)
        self.clustering_interface = clustering_interface
        self.waveform_filtering = waveform_filtering
        self.waveform_mean = waveform_mean
        self.waveform_sd = waveform_sd


@register_class('LFP', CORE_NAMESPACE)
class LFP(MultiContainerInterface):
    """
    LFP data from one or more channels. The electrode map in each published ElectricalSeries will
    identify which channels are providing LFP data. Filter properties should be noted in the
    ElectricalSeries description or comments field.
    """

    __clsconf__ = {
        'attr': 'electrical_series',
        'type': ElectricalSeries,
        'add': 'add_electrical_series',
        'get': 'get_electrical_series',
        'create': 'create_electrical_series',
    }

    __help = ("LFP data from one or more channels. Filter properties "
              "should be noted in the ElectricalSeries")


@register_class('FilteredEphys', CORE_NAMESPACE)
class FilteredEphys(MultiContainerInterface):
    """
    Ephys data from one or more channels that has been subjected to filtering. Examples of filtered
    data include Theta and Gamma (LFP has its own interface). FilteredEphys modules publish an
    ElectricalSeries for each filtered channel or set of channels. The name of each ElectricalSeries is
    arbitrary but should be informative. The source of the filtered data, whether this is from analysis
    of another time series or as acquired by hardware, should be noted in each's
    TimeSeries::description field. There is no assumed 1::1 correspondence between filtered ephys
    signals and electrodes, as a single signal can apply to many nearby electrodes, and one
    electrode may have different filtered (e.g., theta and/or gamma) signals represented.
    """

    __help = ("Ephys data from one or more channels that is subjected to filtering, such as "
              "for gamma or theta oscillations (LFP has its own interface). Filter properties should "
              "be noted in the ElectricalSeries")

    __clsconf__ = {
        'attr': 'electrical_series',
        'type': ElectricalSeries,
        'add': 'add_electrical_series',
        'get': 'get_electrical_series',
        'create': 'create_electrical_series'
    }


@register_class('FeatureExtraction', CORE_NAMESPACE)
class FeatureExtraction(NWBDataInterface):
    """
    Features, such as PC1 and PC2, that are extracted from signals stored in a SpikeEvent
    TimeSeries or other source.
    """

    __nwbfields__ = ('description',
                     {'name': 'electrodes', 'child': True},
                     'times',
                     'features')

    __help = "Container for salient features of detected events"

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data'},
            {'name': 'electrodes', 'type': ElectrodeTableRegion,
             'doc': 'the table region corresponding to the electrodes from which this series was recorded'},
            {'name': 'description', 'type': (list, tuple, np.ndarray, DataChunkIterator),
             'doc': 'A description for each feature extracted', 'ndim': 1},
            {'name': 'times', 'type': ('array_data', 'data'),
             'doc': 'The times of events that features correspond to', 'ndim': 1},
            {'name': 'features', 'type': ('array_data', 'data'),
             'doc': 'Features for each channel', 'ndim': 3},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'FeatureExtraction'})
    def __init__(self, **kwargs):
        # get the inputs
        source, electrodes, description, times, features = popargs(
            'source', 'electrodes', 'description', 'times', 'features', kwargs)

        # Validate the shape of the inputs
        # Validate event times compared to features
        shape_validators = []
        shape_validators.append(ShapeValidator.assertEqualShape(data1=features,
                                                                data2=times,
                                                                axes1=0,
                                                                axes2=0,
                                                                name1='feature_shape',
                                                                name2='times',
                                                                ignore_undetermined=True))
        # Validate electrodes compared to features
        shape_validators.append(ShapeValidator.assertEqualShape(data1=features,
                                                                data2=electrodes,
                                                                axes1=1,
                                                                axes2=0,
                                                                name1='feature_shape',
                                                                name2='electrodes',
                                                                ignore_undetermined=True))
        # Valided description compared to features
        shape_validators.append(ShapeValidator.assertEqualShape(data1=features,
                                                                data2=description,
                                                                axes1=2,
                                                                axes2=0,
                                                                name1='feature_shape',
                                                                name2='description',
                                                                ignore_undetermined=True))
        # Raise an error if any of the shapes do not match
        raise_error = False
        error_msg = ""
        for sv in shape_validators:
            raise_error |= not sv.result
            if not sv.result:
                error_msg += sv.message + "\n"
        if raise_error:
            raise TypeError(error_msg)

        # Initalize the object
        super(FeatureExtraction, self).__init__(source, **kwargs)
        self.electrodes = electrodes
        self.description = description
        self.times = list(times)
        self.features = features
