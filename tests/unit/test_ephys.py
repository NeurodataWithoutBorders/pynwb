import unittest

from pynwb.ecephys import ElectricalSeries, SpikeEventSeries, ElectrodeGroup, Device, EventDetection, EventWaveform, Clustering, ClusterWaveforms, LFP, FilteredEphys, FeatureExtraction

class ElectricalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')
        dev2 = Device('dev2')
        channel_description = ('ch1', 'ch2')
        channel_location = ('lo1', 'lo2')
        channel_filtering = ('fi1', 'fi2')
        channel_coordinates = ('co1', 'co2')
        channel_impedance = ('im1', 'im2')
        elec1 = ElectrodeGroup('elec1', channel_description, channel_location, channel_filtering, channel_coordinates, channel_impedance, 'desc1', 'loc1', dev1)
        elec2 = ElectrodeGroup('elec2', channel_description, channel_location, channel_filtering, channel_coordinates, channel_impedance, 'desc2', 'loc2', dev2)
        elec = (elec1, elec2)
        data = list()

        eS = ElectricalSeries('test_eS', 'a hypothetical source', data, elec, timestamps=list())
        self.assertEqual(eS.name, 'test_eS')
        self.assertEqual(eS.source, 'a hypothetical source')
        self.assertEqual(eS.data, data)
        self.assertEqual(eS.electrode_group, elec)

class SpikeEventSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sES = SpikeEventSeries('test_sES', 'a hypothetical source', list(), list(), timestamps=list())
        self.assertEqual(sES.name, 'test_sES')
        self.assertEqual(sES.source, 'a hypothetical source')

class ElectrodeGroupConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')
        channel_description = ('ch1', 'ch2')
        channel_location = ('lo1', 'lo2')
        channel_filtering = ('fi1', 'fi2')
        channel_coordinates = ('co1', 'co2')
        channel_impedance = ('im1', 'im2')

        elec1 = ElectrodeGroup('elec1', channel_description, channel_location, channel_filtering, channel_coordinates, channel_impedance, 'desc1', 'loc1', dev1)
        self.assertEqual(elec1.name, 'elec1')
        self.assertEqual(elec1.channel_description, channel_description)
        self.assertEqual(elec1.channel_location, channel_location)
        self.assertEqual(elec1.channel_filtering, channel_filtering)
        self.assertEqual(elec1.channel_coordinates, channel_coordinates)
        self.assertEqual(elec1.channel_impedance, channel_impedance)
        self.assertEqual(elec1.description, 'desc1')
        self.assertEqual(elec1.location, 'loc1')
        self.assertEqual(elec1.device, dev1)

class EventDetectionConstructor(unittest.TestCase):
    def test_init(self):
        eS = ElectricalSeries('test_eS', 'a hypothetical source', list(), list(), timestamps=list())

        eD = EventDetection('test_ed', 'detection_method', eS, (1, 2, 3), 'event_times')
        self.assertEqual(eD.source, 'test_ed')
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, 'event_times')
        self.assertEqual(eD.unit, 'Seconds')

class EventWaveformConstructor(unittest.TestCase):
    def test_init(self):
        sES = SpikeEventSeries('test_sES', 'a hypothetical source', list(), list(), timestamps=list())

        ew  = EventWaveform('test_ew', sES)
        self.assertEqual(ew.source, 'test_ew')
        self.assertEqual(ew.spike_event_series, sES)

class ClusteringConstructor(unittest.TestCase):
    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]

        cc = Clustering('test_cc', 'description', num, peak_over_rms, times)
        self.assertEqual(cc.source, 'test_cc')
        self.assertEqual(cc.description, 'description')
        self.assertEqual(cc.num, num)
        self.assertEqual(cc.peak_over_rms, peak_over_rms)
        self.assertEqual(cc.times, times)

class ClusterWaveformsConstructor(unittest.TestCase):
    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]
        cc = Clustering('test_cc', 'description', num, peak_over_rms, times)

        means = [7.3, 7.3]
        stdevs = [8.3, 8.3]

        cw = ClusterWaveforms('test_cw', cc, 'filtering', means, stdevs)
        self.assertEqual(cw.source, 'test_cw')
        self.assertEqual(cw.clustering_interface, cc)
        self.assertEqual(cw.waveform_filtering, 'filtering')
        self.assertEqual(cw.waveform_mean, means)
        self.assertEqual(cw.waveform_sd, stdevs)

class LFPConstructor(unittest.TestCase):
    def test_init(self):
        eS = ElectricalSeries('test_eS', 'a hypothetical source', list(), list(), timestamps=list())

        lfp = LFP('test_lfp', eS)
        self.assertEqual(lfp.source, 'test_lfp')
        self.assertEqual(lfp.electrical_series, eS)

class FilteredEphysConstructor(unittest.TestCase):
    def test_init(self):
        eS = ElectricalSeries('test_eS', 'a hypothetical source', list(), list(), timestamps=list())

        fe = FilteredEphys('test_fe', eS)
        self.assertEqual(fe.source, 'test_fe')
        self.assertEqual(fe.electrical_series, eS)

class FeatureExtractionConstructor(unittest.TestCase):
    def test_init(self):
        event_times = [ 1 ]
        electrodes  = [ 'elec1', 'elec2' ]
        description = [ 'desc1', 'desc2', 'desc3' ]
        features = [[[0,1,2], [3,4,5]]]
        fe = FeatureExtraction('test_fe', electrodes, description, event_times, features)
        self.assertEqual(fe.source, 'test_fe')

    def test_invalid_init_mismatched_event_times(self):
        event_times = []  # Need 1 event time but give 0
        electrodes  = [ 'elec1', 'elec2' ]
        description = [ 'desc1', 'desc2', 'desc3' ]
        features = [[[0,1,2], [3,4,5]]]
        self.assertRaises(TypeError, FeatureExtraction, 'test_fe', electrodes, description, event_times, features)

    def test_invalid_init_mismatched_electrodes(self):
        event_times = [ 1 ]
        electrodes  = [ 'elec1', ]  # Need 2 electrodes but give 1
        description = [ 'desc1', 'desc2', 'desc3' ]
        features = [[[0,1,2], [3,4,5]]]
        self.assertRaises(TypeError, FeatureExtraction, 'test_fe', electrodes, description, event_times, features)

    def test_invalid_init_mismatched_description(self):
        event_times = [ 1 ]
        electrodes  = [ 'elec1', 'elec2' ]
        description = [ 'desc1', 'desc2', 'desc3', 'desc4' ]  # Need 3 descriptions but give 4
        features = [[[0,1,2], [3,4,5]]]
        self.assertRaises(TypeError, FeatureExtraction, 'test_fe', electrodes, description, event_times, features)

    def test_invalid_init_mismatched_description(self):
        event_times = [ 1 ]
        electrodes  = [ 'elec1', 'elec2' ]
        description = [ 'desc1', 'desc2', 'desc3' ]
        features = [[0,1,2], [3,4,5]]  # Need 3D feature array but give only 2D array
        self.assertRaises(TypeError, FeatureExtraction, 'test_fe', electrodes, description, event_times, features)


if __name__ == '__main__':
    unittest.main()
