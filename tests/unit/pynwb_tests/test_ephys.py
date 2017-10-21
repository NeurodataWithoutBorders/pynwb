import unittest

import numpy as np

from pynwb.ecephys import *

def make_electrode_table():
    table = ElectrodeTable('test_table')
    dev1 = Device('dev1', 'a test source')
    group = ElectrodeGroup('tetrode1', 'a test source', 'tetrode description', 'tetrode location', dev1)
    table.add_row(1, 1.0, 2.0, 3.0, -1.0, 'CA1', 'none', 'first channel of tetrode', group)
    table.add_row(2, 1.0, 2.0, 3.0, -2.0, 'CA1', 'none', 'second channel of tetrode', group)
    table.add_row(3, 1.0, 2.0, 3.0, -3.0, 'CA1', 'none', 'third channel of tetrode', group)
    table.add_row(4, 1.0, 2.0, 3.0, -4.0, 'CA1', 'none', 'fourth channel of tetrode', group)
    return table

class ElectricalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        data =  list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        eS = ElectricalSeries('test_eS', 'a hypothetical source', data, region, timestamps=ts)
        self.assertEqual(eS.name, 'test_eS')
        self.assertEqual(eS.source, 'a hypothetical source')
        self.assertEqual(eS.data, data)
        self.assertEqual(eS.timestamps, ts)

class SpikeEventSeriesConstructor(unittest.TestCase):
    def test_init(self):
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [1,3], 'the second and fourth electrodes')
        data = np.zeros(10)
        timestamps = np.arange(10)
        sES = SpikeEventSeries('test_sES', 'a hypothetical source', data, timestamps, region)
        self.assertEqual(sES.name, 'test_sES')
        self.assertEqual(sES.source, 'a hypothetical source')
        #self.assertListEqual(sES.data, data)
        np.testing.assert_array_equal(sES.data, data)
        np.testing.assert_array_equal(sES.timestamps, timestamps)

class ElectrodeGroupConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1', 'a test source')
        group = ElectrodeGroup('elec1', 'a test source', 'electrode description', 'electrode location', dev1)
        self.assertEqual(group.name, 'elec1')
        self.assertEqual(group.description, 'electrode description')
        self.assertEqual(group.location, 'electrode location')
        self.assertEqual(group.device, dev1)

class EventDetectionConstructor(unittest.TestCase):
    def test_init(self):
        data =  list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        eS = ElectricalSeries('test_eS', 'a hypothetical source', data, region, timestamps=ts)
        eD = EventDetection('test_ed', 'detection_method', eS, (1, 2, 3), (0.1, 0.2, 0.3))
        self.assertEqual(eD.source, 'test_ed')
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, (0.1, 0.2, 0.3))
        self.assertEqual(eD.unit, 'Seconds')

class EventWaveformConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1', 'a test source')
        group = ElectrodeGroup('tetrode1', 'a test source', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        sES = SpikeEventSeries('test_sES', 'a hypothetical source', list(range(10)), list(range(10)), region)

        ew  = EventWaveform('test_ew', sES)
        self.assertEqual(ew.source, 'test_ew')
        self.assertEqual(ew.spike_event_series, [sES])

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
        dev1 = Device('dev1', 'a test source')
        group = ElectrodeGroup('tetrode1', 'a test source', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        eS = ElectricalSeries('test_eS', 'a hypothetical source', [0,1,2,3], region, timestamps=[0.1,0.2,0.3,0.4])
        lfp = LFP('test_lfp', eS)
        self.assertEqual(lfp.source, 'test_lfp')
        self.assertEqual(lfp.electrical_series, eS)

class FilteredEphysConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1', 'a test source')
        group = ElectrodeGroup('tetrode1', 'a test source', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        eS = ElectricalSeries('test_eS', 'a hypothetical source', [0,1,2,3], region, timestamps=[0.1,0.2,0.3,0.4])
        fe = FilteredEphys('test_fe', eS)
        self.assertEqual(fe.source, 'test_fe')
        self.assertEqual(fe.electrical_series, eS)

class FeatureExtractionConstructor(unittest.TestCase):
    def test_init(self):
        event_times = [ 1.9, 3.5 ]
        table = make_electrode_table()
        region = ElectrodeTableRegion(table, [0,2], 'the first and third electrodes')
        description = [ 'desc1', 'desc2', 'desc3' ]
        features = [[[0,1,2], [3,4,5]], [[6,7,8], [9,10,11]]]
        fe = FeatureExtraction('test_fe', region, description, event_times, features)
        self.assertEqual(fe.source, 'test_fe')
        self.assertEqual(fe.description, description)
        self.assertEqual(fe.times, event_times)
        self.assertEqual(fe.features, features)

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
