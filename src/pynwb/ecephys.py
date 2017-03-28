from .base import TimeSeries, Interface, _default_resolution, _default_conversion
from .core import docval, popargs, NWBContainer, DataChunkIterator, ShapeValidator

import numpy as np
from collections import Iterable

class ElectricalSeries(TimeSeries):
    """
    Stores acquired voltage data from extracellular recordings. The data field of an ElectricalSeries
    is an int or float array storing data in Volts. TimeSeries::data array structure: [num times] [num
    channels] (or [num_times] for single electrode).
    """

    __nwbfields__ = ('electrodes',)

    __ancestry = "TimeSeries,ElectricalSeries"
    __help = "Stores acquired voltage data from extracellular recordings."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},

            {'name': 'electrodes', 'type': (list, tuple), 'doc': 'the names of the electrode groups, or the ElectrodeGroup objects that each channel corresponds to'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, electrodes, data = popargs('name', 'source', 'electrodes', 'data', kwargs)
        super(ElectricalSeries, self).__init__(name, source, data, 'volt', **kwargs)
        self.electrodes = tuple(electrodes)


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
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},

            {'name': 'electrodes', 'type': (list, tuple), 'doc': 'the names of the electrode groups, or the ElectrodeGroup objects that each channel corresponds to'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, electrodes, data = popargs('name', 'source', 'electrodes', 'data', kwargs)
        super(SpikeEventSeries, self).__init__(name, source, electrodes, data, **kwargs)

class ElectrodeGroup(NWBContainer):
    __nwbfields__ = ('name',
                     'description',
                     'device',
                     'location',
                     'physical_location',
                     'impedance')

    @docval({'name': 'name', 'type': (str, int), 'doc': 'the name of this electrode'},
            {'name': 'coord', 'type': (tuple, list, np.ndarray), 'doc': 'the x,y,z coordinates of this electrode'},
            {'name': 'desc', 'type': str, 'doc': 'a description for this electrode'},
            {'name': 'dev', 'type': str, 'doc': 'the device this electrode was recorded from on'},
            {'name': 'loc', 'type': str, 'doc': 'a description of the location of this electrode'},
            {'name': 'imp', 'type': float, 'doc': 'the impedance of this electrode', 'default': -1.0},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, coord, desc, dev, loc, imp, parent = popargs("name", "coord", "desc", "dev", "loc", "imp", "parent", kwargs)
        super(ElectrodeGroup, self).__init__(parent=parent)
        self.name = name
        self.physical_location = coord
        self.description = desc
        self.device = dev
        self.location = loc
        self.impedance = imp

class EventDetection(Interface):
    """
    Detected spike events from voltage trace(s).
    """

    __nwbfields__ =  ('detection_method',
                      'source_indices',
                      'event_times',
                      'data')

    _help_statement = ("Description of how events were detected, such as voltage "
                       "threshold, or dV/dT threshold, as well as relevant values.")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': ElectricalSeries, 'doc': 'the source electrophysiology data'},
            {'name': 'detection_method', 'type': str, 'doc': 'a description of how events were detected'},
            {'name': 'event_times', 'type': Iterable, 'doc': 'timestamps of events, in Seconds'})
    def __init___(self, **kwargs):
        source, data, detection_method, event_times = popargs('source', 'data', 'detection_method', 'event_times', kwargs)
        super(EventDetection, self).__init__(source, **kwargs)
        self.detection_method = detection_method
        self.event_times = event_times
        self.source_indices = list() # I think we should calculate this under the hood
        # do not set parent, since this is a link
        self.data = data

    #def add_event(self, idx, time):
    #    self.source_indices.append(idx)
    #    self.event_time.append(time)

class EventWaveform(Interface):
    """
    Spike data for spike events detected in raw data
    stored in this NWBFile, or events detect at acquisition
    """

    __nwbfields__ = ('data',)

    __help = "Waveform of detected extracellularly recorded spike events"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': SpikeEventSeries, 'doc': 'spiking event data'})
    def __init__(self, **kwargs):
        source, data = popargs('source', 'data', kwargs)
        super(EventWaveform, self).__init__(source, **kwargs)
        data.parent = self
        self.data = data

class Clustering(Interface):
    """
    Specifies cluster event times and cluster metric for maximum ratio of waveform peak to RMS on any channel in cluster.
    """

    __nwbfields__  = ('cluster_times',
                      'cluster_ids',
                      'peak_over_rms')

    __help = ("Clustered spike data, whether from automatic clustering "
             "tools (eg, klustakwik) or as a result of manual sorting")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'cluster_times', 'type': (tuple, list, np.ndarray), 'doc': 'times of clustered events'},
            {'name': 'cluster_ids', 'type': (tuple, list, np.ndarray), 'doc': 'description of clusters and/or clustering method'},
            {'name': 'peak_over_rms', 'type': (tuple, list, np.ndarray), 'doc': 'maximum ratio of waveform peak to RMS on any channel in the cluster'})
    def __init__(self, **kwargs):
        source, cluster_times, cluster_ids, peak_over_rms = popargs('source', 'cluster_times', 'cluster_ids', 'peak_over_rms', kwargs)
        super(Clustering, self).__init__(source, **kwargs)
        self.cluster_times = cluster_times
        self.cluster_ids = cluster_ids
        self.peak_over_rms = list(peak_over_rms)

class ClusterWaveform(Interface):
    """
    Describe cluster waveforms by mean and standard deviation for at each sample.
    """

    __nwbfields__ = ('clustering',
                     'filtering',
                     'means',
                     'stdevs')

    __help = ("Mean waveform shape of clusters. Waveforms should be "
             "high-pass filtered (ie, not the same bandpass filter "
             "used waveform analysis and clustering)")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'clustering', 'type': Clustering, 'doc': 'the clustered spike data used as input for computing waveforms'},
            {'name': 'filtering', 'type': str, 'doc': 'filter applied to data before calculating mean and standard deviation'},
            {'name': 'means', 'type': Iterable, 'doc': 'the mean waveform for each cluster'},
            {'name': 'stdevs', 'type': Iterable, 'doc': 'the standard deviations of waveforms for each cluster'})
    def __init__(self, **kwargs):
        source, clustering, filtering, means, stdevs = popargs('source', 'clustering', 'filtering', 'means', 'stdevs', kwargs)
        super(ClusterWaveform, self).__init__(source, **kwargs)
        self.clustering = clustering
        self.filtering = filtering
        self.means = means
        self.stdevs = stdevs

class LFP(Interface):
    """
    LFP data from one or more channels. The electrode map in each published ElectricalSeries will
    identify which channels are providing LFP data. Filter properties should be noted in the
    ElectricalSeries description or comments field.
    """

    __nwbfields__ = ('data',)

    __help = ("LFP data from one or more channels. Filter properties "
             "should be noted in the ElectricalSeries")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': ElectricalSeries, 'doc': 'LFP electrophysiology data'})
    def __init__(self, **kwargs):
        source, data = popargs('source', 'data', kwargs)
        super(LFP, self).__init__(source, **kwargs)
        data.parent = self
        self.data = data

class FilteredEphys(Interface):
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

    __nwbfields__ = ('_ElectricalSeries',)

    __help = ("Ephys data from one or more channels that is subjected to filtering, such as "
             "for gamma or theta oscillations (LFP has its own interface). Filter properties should "
             "be noted in the ElectricalSeries")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_ElectricalSeries', 'type': ElectricalSeries, 'doc': 'filtered electrophysiology data'})
    def __init__(self, **kwargs):
        source, _ElectricalSeries = popargs('source', '_ElectricalSeries', kwargs)
        super(FilteredEphys, self).__init__(source, **kwargs)
        _ElectricalSeries.parent = self
        self._ElectricalSeries = _ElectricalSeries

class FeatureExtraction(Interface):
    """
    Features, such as PC1 and PC2, that are extracted from signals stored in a SpikeEvent
    TimeSeries or other source.
    """

    __nwbfields__ = ('description',
                     'electrodes',
                     'event_times',
                     'features')

    __help = "Container for salient features of detected events"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'electrodes', 'type': (list, tuple, np.ndarray, DataChunkIterator), 'doc': 'the electrode groups for each channel from which features were extracted'},
            {'name': 'description', 'type': (list, tuple, np.ndarray, DataChunkIterator), 'doc': 'a description for each feature extracted'},
            {'name': 'event_times', 'type': (list, tuple, np.ndarray, DataChunkIterator), 'doc': 'the times of events that features correspond to'},
            {'name': 'features', 'type': (list, tuple, np.ndarray, DataChunkIterator), 'doc': 'features for each channel'})
    def __init__(self, **kwargs):
        # get the inputs
        source, electrodes, description, event_times, features = popargs('source', 'electrodes', 'description', 'event_times', 'features', kwargs)

        # Validate the shape of the inputs
        # Validate the shape of the features array
        features_shape = ShapeValidator.get_data_shape(features)
        if features_shape is not None and len(features_shape) != 3:
            raise ValueError("incorrect dimensions: features must be a 3D array.")
        # Validate event times compared to features
        shape_validators = []
        shape_validators.append(ShapeValidator.assertEqualShape(data1=features,
                                                                data2=event_times,
                                                                axes1=0,
                                                                axes2=0,
                                                                name1='feature_shape',
                                                                name2='event_times',
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
            raise ValueError(error_msg)


        # Initalize the object
        super(FeatureExtraction, self).__init__(source, **kwargs)
        self.fields['electrodes'] = electrodes
        self.fields['description'] = description
        self.fields['event_times'] = list(event_times)
        self.fields['features'] = features

