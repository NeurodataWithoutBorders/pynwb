from .base import TimeSeries, Interface, _default_resolution, _default_conversion
from .core import docval, getargs, popargs, NWBContainer

import numpy as np
from collections import Iterable

class ElectricalSeries(TimeSeries):
    
    __nwbfields__ = ('electrodes',)

    _ancestry = "TimeSeries,ElectricalSeries"
    __help = "Stores acquired voltage data from extracellular recordings"

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
        """ 
        Create a new ElectricalSeries dataset
        """
        name, source, electrodes, data = popargs('name', 'source', 'electrodes', 'data', kwargs)
        super(ElectricalSeries, self).__init__(name, source, data, 'volt', **kwargs)
        self.electrodes = tuple(electrodes)


class SpikeEventSeries(ElectricalSeries):

    _ancestry = "TimeSeries,ElectricalSeries,SpikeSeries"

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
            {'name': 'imp', 'type': float, 'doc': 'the impedance of this electrode', 'default': -1.0})
    def __init__(self, **kwargs):
        name, coord, desc, dev, loc, imp, parent = getargs("name", "coord", "desc", "dev", "loc", "imp", "parent", kwargs)
        super(ElectrodeGroup, self).__init__(parent=parent)
        self.name = name
        self.physical_location = coord
        self.description = desc
        self.device = dev
        self.location = loc
        self.impedance = imp

class EventDetection(Interface):
    __nwbfields__ =  ('detection_method',
                      'source_indices',
                      'event_times',
                      'data')

    _help_statement = ("Description of how events were detected, such as voltage "
                       "threshold, or dV/dT threshold, as well as relevant values.")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': ElectricalSeries, 'doc': 'the source electrophysiology data'},
            {'name': 'detection_method', 'type': str, 'doc': 'a description of how events were detected'},
            {'name': 'event_times', 'type': str, 'doc': 'timestamps of events'})
    def __init___(self, **kwargs):
                  #source_indices=list()):
        source, data, detection_method, event_times = getargs('source', 'voltage_data_ts', 'detection_method', 'event_times', kwargs)
        super(EventDetection, self).__init__(source)
        self.detection_method = detection_method
        self.event_times = event_times
        self.source_indices = list() # I think we should calculate this under the hood
        # do not set parent, since this is a link
        self.data = data

    #def add_event(self, idx, time):
    #    self.source_indices.append(idx)
    #    self.event_time.append(time)

class EventWaveform(Interface):
    """Spike data for spike events detected in raw data
    stored in this NWBFile, or events detect at acquisition
    """
    __nwbfields__ = ('data',)

    __help = "Waveform of detected extracellularly recorded spike events"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': SpikeEventSeries, 'doc': 'spiking event data'})
    def __init__(self, **kwargs):
        source, data = getargs('source', 'spike_data_ts', kwargs)
        super(EventWaveform, self).__init__(source)
        spike_data_ts.parent = self
        self.data = data
        

class Clustering(Interface):
    """Specifies cluster event times and cluster
       metric for maximum ratio of waveform peak to
       RMS on any channel in cluster.
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
        """ Conveninece function to set interface values. Includes
            sanity checks for array lengths
        """
        source, cluster_times, cluster_ids, peak_over_rms = getargs('source', 'cluster_times', 'cluster_ids', 'peak_over_rms', kwargs)
        super(Clustering, self).__init__(source)
        self.cluster_times = cluster_times
        self.cluster_ids = cluster_ids
        self.peak_over_rms = dict(enumerate(peak_over_rms))

#    def add_event(self, cluster_id, time):
#        self.nums.append(cluster_num)
#        self.times.append(time)
#
#    def add_cluster(self, cluster_num, peak_over_rms):
#        self.peak_over_rms[cluster_num] = peak_over_rms


class ClusterWaveform(Interface):
    """Describe cluster waveforms by mean and standard deviation
       for at each sample.
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
        source, clustering, filtering, means, stdevs = getargs('source', 'clustering', 'filtering', 'means', 'stdevs', kwargs)
        super(ClusterWaveform, self).__init__(source)
        self.clustering = clustering
        self.filtering = filtering
        self.means = means
        self.sds = stdevs

class LFP(Interface):

    __nwbfields__ = ('data',)

    __help = ("LFP data from one or more channels. Filter properties "
             "should be noted in the ElectricalSeries")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': ElectricalSeries, 'doc': 'LFP electrophysiology data'})
    def __init__(self, **kwargs):
        source, data = getargs('source', 'data', kwargs)
        data.parent = self
        super(LFP, self).__init__(source)
        self.data = data

class FilteredEphys(Interface):

    __nwbfields__ = ('data',)

    __help = ("Ephys data from one or more channels that is subjected to filtering, such as "
             "for gamma or theta oscillations (LFP has its own interface). Filter properties should "
             "be noted in the ElectricalSeries")

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'data', 'type': ElectricalSeries, 'doc': 'filtered electrophysiology data'})
    def __init__(self, **kwargs):
        source, data = getargs('source', 'data', kwargs)
        data.parent = self
        super(FilteredEphys, self).__init__(source)
        self.data = data


class FeatureExtraction(Interface):

    __nwbfields__ = ('description',
                     'electrodes',
                     'event_times',
                     'features')

    __help = "Container for salient features of detected events"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'electrodes', 'type': (list, tuple), 'doc': 'the electrode groups for each channel from which features were extracted'},
            {'name': 'description', 'type': (list, tuple), 'doc': 'a description for each feature extracted'},
            {'name': 'event_times', 'type': (list, tuple, np.ndarray), 'doc': 'the times of events that features correspond to'},
            {'name': 'features', 'type': (list, tuple, np.ndarray), 'doc': 'features for each channel'})
    def __init__(self, **kwargs):
        source, electrodes, description, event_times, features = getargs('source', 'electrodes', 'description', 'event_times', 'features', kwargs)
        if len(features) != len(electrodes):
            raise ValueError("incorrect dimensions: features -  must have one value per channel. Got %d, expected %d" % (len(features), len(self._electrodes)))
        if len(features[0]) != len(description):
            raise ValueError("incorrect dimensions: features -  must have one value per feature. Got %d, expected %d" % (len(features[0]), len(self._description)))
        super(FeatureExtraction, self).__init__(source)
        self.fields['electrodes'] = electrodes
        self.fields['description'] = description
        self.fields['event_times'] = list(event_times)
        self.fields['features'] = list(features)

    #def add_event_feature(self, time, features):
    #    self._features.append(features)
    #    self._event_times.append(time)
