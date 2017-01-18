from pynwb.core import docval, getargs
from pynwb.ui.container import nwbproperties, NWBContainer
#from pynwb.ui.module import Interface
from pynwb.ui.iface import Interface




__std_fields = ('name',
                'description',
                'device',
                'location',
                'physical_location',
                'impedance')
@nwbproperties(*__std_fields)
class ElectrodeGroup(NWBContainer):

    @docval({'name': 'name', 'type': (str, int), 'doc': 'the name of this electrode'},
            {'name': 'coord', 'type': tuple, 'doc': 'the x,y,z coordinates of this electrode'},
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

__event_detection_std_fields = ('detection_method',
                                'source_indices',
                                'event_times',
                                'voltage_data')
@nwbproperties(*__event_detection_std_fields)
class EventDetection(Interface):

    _help_statement = ("Description of how events were detected, such as voltage "
                       "threshold, or dV/dT threshold, as well as relevant values.")

    _interface = "EventDetection"

    def __init___(self, voltage_data_ts, detection_method,
                  source_indices=list(), event_times=list()):
        super(EventDetection, self).__init__()
        self._detection_method = detection_method
        self._source_indices = source_indices
        self._event_times = event_times
        # do not set parent, since this is a link
        self._voltage_data = voltage_data_ts

    def add_event(self, idx, time):
        self._source_indices.append(idx)
        self._event_time.append(time)

__event_waveform_std_fields = ('spike_data',)
@nwbproperties(*__event_waveform_std_fields)                               
class EventWaveform(Interface):
    """Spike data for spike events
    """

    _help_statement = "Waveform of detected extracellularly recorded spike events"

    _interface = "EventWaveform"

    def __init__(self, spike_data_ts=None):
        super(EventWaveform, self).__init__()
        self._spike_data = spike_data_ts
        self._spike_data.parent = self
        

__clustering_std_fields = ('cluster_times',
                           'cluster_ids')
@nwbproperties(*__clustering_std_fields)
class Clustering(Interface):
    """Specifies cluster event times and cluster
       metric for maximum ratio of waveform peak to
       RMS on any channel in cluster.
    """

    _help = ("Clustered spike data, whether from automatic clustering " 
             "tools (eg, klustakwik) or as a result of manual sorting")

    _interface = "Clustering"


    def __init__(self, cluster_times=list(), 
                 cluster_ids=list(), peak_over_rms=list()):
        """ Conveninece function to set interface values. Includes
            sanity checks for array lengths

            Arguments:
                *times* (double array) Times of clustered events, in
                seconds. This may be a link to times field in associated
                FeatureExtraction module. Array structure: [num events]

                *num* (int array) Cluster number for each event Array 
                structure: [num events]

                *description* (text)  Description of clusters or 
                clustering (e.g., cluster 0 is electrical noise, 
                clusters curated using Klusters, etc)

                *peak_over_rms* (float array) Maximum ratio of waveform 
                peak to RMS on any channel in the cluster (provides a 
                basic clustering metric).  Array structure: [num clusters]

            Returns:
                *nothing*
        """
        super(Clustering, self).__init__()
        self._cluster_times = cluster_times
        self._cluster_ids = cluster_ids
        self._peak_over_rms = dict(enumerate(peak_over_rms))

    def add_event(self, cluster_id, time):
        self.nums.append(cluster_num)
        self.times.append(time)

    def add_cluster(self, cluster_num, peak_over_rms):
        self.peak_over_rms[cluster_num] = peak_over_rms


__cluster_waveform_std_fields = ('filtering',
                                 'wf_mean',
                                 'wf_sd')
@nwbproperties(*__cluster_waveform_std_fields)
class ClusterWaveform(Interface):
    """Describe cluster waveforms by mean and standard deviation
       for at each sample.
    """
    
    _help_statement = ("Mean waveform shape of clusters. Waveforms should be "
                       "high-pass filtered (ie, not the same bandpass filter "
                       "used waveform analysis and clustering)")

    _interface = "ClusterWaveform"
    
    def __init__(self, clustering, filtering, wf_means=list(), wf_sds=list()):
        super(ClusterWaveform, self).__init__()
        self._clustering = clustering
        self._filtering = filtering
        self._wf_means = list()
        self._wf_sds = list()

    def add_waveform(self, sample_means, sample_sds):
        self.wf_means.append(sample_means)
        self.wf_sds.append(sample_sds)

__lfp_std_fields = ('lfp_data',)
@nwbproperties(*__lfp_std_fields)
class LFP(Interface):

    _help_statement =("LFP data from one or more channels. Filter properties "
                      "should be noted in the ElectricalSeries")

    _interface = "LFP"

    def __init__(self, lfp_ts=None):
        super(LFP, self).__init__()
        if lfp_ts:
            self.add_lfp_data(lfp_ts)
        else:
            self._lfp_data = None

    def add_lfp_data(self, lfp_ts):
        self._lfp_data = lfp_ts
        self._lfp_data.parent = self

__filter_ephys_std_fields = ('ephys_data',)
@nwbproperties(*__filter_ephys_std_fields)
class FilteredEphys(Interface):

    _help_statement = ("Ephys data from one or more channels that is subjected to filtering, such as "
                       "for gamma or theta oscillations (LFP has its own interface). Filter properties should "
                       "be noted in the ElectricalSeries")
    _interface = "FilteredEphys"

    def __init__(self, ephys_ts=None):
        super(FilteredEphys, self).__init__()
        if ephys_ts:
            self.add_ephys_data(ephys_ts)
        else:
            self._ephys_data = None

    def add_lfp_data(self, ephys_ts):
        self._ephys_data = ephys_ts
        self._ephys_data.parent = self
        

__feat_extr_std_fields = ('description',
                          'electrodes',
                          'event_times',
                          'features')
@nwbproperties(*__filter_ephys_std_fields)
class FeatureExtraction(Interface):


    _help_statement = "Container for salient features of detected events"

    _interface = "FeatureExtraction"

    def __init__(self, electrodes, description, event_times=list(), features=list()):
        super(FeatureExtraction, self).__init__()
        self._electrodes = electrodes
        self._description = description
        self._event_times = event_times
        self._features = features

    def add_event_feature(self, time, features):
        if len(features) != len(self._electrodes):
            raise ValueError("incorrent dimensions: features -  must have one value per channel. Got %d, expected %d" % (len(features), len(self._electrodes)))
        if len(features[0]) != len(self._description):
            raise ValueError("incorrent dimensions: features -  must have one value per feature. Got %d, expected %d" % (len(features[0]), len(self._description)))
        self._features.append(features)
        self._event_times.append(time)
