import unittest

from pynwb.ecephys import ElectricalSeries, SpikeEventSeries, ElectrodeGroup, EventDetection, EventWaveform, Clustering, ClusterWaveforms, LFP, FilteredEphys, FeatureExtraction

class ElectricalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        data = list()
        coord = (1, 2, 3)
        elec1 = ElectrodeGroup('name', coord, 'desc', 'dev', 'loc', 1.0)
        elec2 = ElectrodeGroup('name', coord, 'desc', 'dev', 'loc', 2.0)
        elec = (elec1, elec2)

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
    def setUp(self):
        #print(ElectrodeGroup.__init__.docval)
        self.name = 'my_group'
        self.coord = (1.1, 2.2, 3.3)
        self.desc = "an example electrode group"
        self.dev = "my favorite device"
        self.loc = "my favorote brain location"
        self.eg = ElectrodeGroup(self.name,
                                 self.coord,
                                 self.desc,
                                 self.dev,
                                 self.loc)

    def test_impedance(self):
        self.assertEqual(self.eg.impedance, -1)

    def test_name(self):
        self.assertEqual(self.eg.name, self.name)

    def test_physical_location(self):
        self.assertTupleEqual(self.eg.physical_location, self.coord)

    def test_description(self):
        self.assertEqual(self.eg.description, self.desc)

    def test_device(self):
        self.assertEqual(self.eg.device, self.dev)

    def test_location(self):
        self.assertEqual(self.eg.location, self.loc)

class EventDetectionConstructor(unittest.TestCase):
    def test_init(self):
        eS = ElectricalSeries('test_eS', 'a hypothetical source', list(), list(), timestamps=list())

        eD = EventDetection('test_ed', 'detection_method', eS, (1, 2, 3), 'event_times')
        self.assertEqual(eD.source, 'test_ed')
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, 'event_times')

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
