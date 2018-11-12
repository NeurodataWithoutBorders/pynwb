import unittest

import numpy as np

from pynwb.ecephys import ElectricalSeries, SpikeEventSeries, EventDetection, Clustering, EventWaveform,\
                          ClusterWaveforms, LFP, FilteredEphys, FeatureExtraction, ElectrodeGroup
from pynwb.device import Device
from pynwb.file import ElectrodeTable
from pynwb.core import DynamicTableRegion


def make_electrode_table():
    table = ElectrodeTable()
    dev1 = Device('dev1')  # noqa: F405
    group = ElectrodeGroup('tetrode1', 'tetrode description', 'tetrode location', dev1)  # noqa: F405
    table.add_row(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none',
                  group=group, group_name='tetrode1')
    table.add_row(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none',
                  group=group, group_name='tetrode1')
    table.add_row(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none',
                  group=group, group_name='tetrode1')
    table.add_row(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none',
                  group=group, group_name='tetrode1')
    return table


class ElectricalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries('test_eS', data, region, timestamps=ts)  # noqa: F405
        self.assertEqual(eS.name, 'test_eS')
        self.assertEqual(eS.data, data)
        self.assertEqual(eS.timestamps, ts)


class SpikeEventSeriesConstructor(unittest.TestCase):
    def test_init(self):
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [1, 3], 'the second and fourth electrodes', table)
        data = np.zeros(10)
        timestamps = np.arange(10)
        sES = SpikeEventSeries('test_sES', data, timestamps, region)  # noqa: F405
        self.assertEqual(sES.name, 'test_sES')
        # self.assertListEqual(sES.data, data)
        np.testing.assert_array_equal(sES.data, data)
        np.testing.assert_array_equal(sES.timestamps, timestamps)


class ElectrodeGroupConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405
            'elec1', 'electrode description', 'electrode location', dev1)
        self.assertEqual(group.name, 'elec1')
        self.assertEqual(group.description, 'electrode description')
        self.assertEqual(group.location, 'electrode location')
        self.assertEqual(group.device, dev1)


class EventDetectionConstructor(unittest.TestCase):
    def test_init(self):
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries('test_eS', data, region, timestamps=ts)  # noqa: F405
        eD = EventDetection('detection_method', eS, (1, 2, 3), (0.1, 0.2, 0.3))  # noqa: F405
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, (0.1, 0.2, 0.3))
        self.assertEqual(eD.unit, 'Seconds')


class EventWaveformConstructor(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405, F841
            'tetrode1', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        sES = SpikeEventSeries(  # noqa: F405
            'test_sES', list(range(10)), list(range(10)), region)

        ew = EventWaveform(sES)  # noqa: F405
        self.assertEqual(ew.spike_event_series['test_sES'], sES)
        self.assertEqual(ew['test_sES'], ew.spike_event_series['test_sES'])


class ClusteringConstructor(unittest.TestCase):
    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]

        cc = Clustering('description', num, peak_over_rms, times)  # noqa: F405
        self.assertEqual(cc.description, 'description')
        self.assertEqual(cc.num, num)
        self.assertEqual(cc.peak_over_rms, peak_over_rms)
        self.assertEqual(cc.times, times)


class ClusterWaveformsConstructor(unittest.TestCase):
    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]
        cc = Clustering('description', num, peak_over_rms, times)  # noqa: F405

        means = [[7.3, 7.3]]
        stdevs = [[8.3, 8.3]]

        cw = ClusterWaveforms(cc, 'filtering', means, stdevs)  # noqa: F405
        self.assertEqual(cw.clustering_interface, cc)
        self.assertEqual(cw.waveform_filtering, 'filtering')
        self.assertEqual(cw.waveform_mean, means)
        self.assertEqual(cw.waveform_sd, stdevs)


class LFPTest(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405, F841
            'tetrode1', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries(  # noqa: F405
            'test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        lfp = LFP(eS)  # noqa: F405
        self.assertEqual(lfp.electrical_series.get('test_eS'), eS)
        self.assertEqual(lfp['test_eS'], lfp.electrical_series.get('test_eS'))

    def test_add_electrical_series(self):
        lfp = LFP()  # noqa: F405
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405, F841
            'tetrode1', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries(  # noqa: F405
            'test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        lfp.add_electrical_series(eS)
        self.assertEqual(lfp.electrical_series.get('test_eS'), eS)
        self.assertEqual(lfp['test_eS'], lfp.electrical_series.get('test_eS'))


class FilteredEphysTest(unittest.TestCase):
    def test_init(self):
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405, F841
            'tetrode1', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries(  # noqa: F405
            'test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        fe = FilteredEphys(eS)  # noqa: F405
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))

    def test_add_electrical_series(self):
        fe = FilteredEphys()  # noqa: F405
        dev1 = Device('dev1')  # noqa: F405
        group = ElectrodeGroup(  # noqa: F405, F841
            'tetrode1', 'tetrode description', 'tetrode location', dev1)
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        eS = ElectricalSeries(  # noqa: F405
            'test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        fe.add_electrical_series(eS)
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))


class FeatureExtractionConstructor(unittest.TestCase):
    def test_init(self):
        event_times = [1.9, 3.5]
        table = make_electrode_table()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]]
        fe = FeatureExtraction(region, description, event_times, features)   # noqa: F405
        self.assertEqual(fe.description, description)
        self.assertEqual(fe.times, event_times)
        self.assertEqual(fe.features, features)

    def test_invalid_init_mismatched_event_times(self):
        event_times = []  # Need 1 event time but give 0
        table = make_electrode_table()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(
            ValueError, FeatureExtraction, electrodes,
            description, event_times, features)

    def test_invalid_init_mismatched_electrodes(self):
        event_times = [1]
        table = make_electrode_table()
        electrodes = DynamicTableRegion('electrodes', [0], 'the first electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, electrodes,
                          description, event_times, features)

    def test_invalid_init_mismatched_description(self):
        event_times = [1]
        table = make_electrode_table()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3', 'desc4']  # Need 3 descriptions but give 4
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(
            ValueError, FeatureExtraction, electrodes, description, event_times, features)

    def test_invalid_init_mismatched_description2(self):  # noqa: F811
        event_times = [1]
        table = make_electrode_table()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[0, 1, 2], [3, 4, 5]]  # Need 3D feature array but give only 2D array
        self.assertRaises(ValueError, FeatureExtraction,  # noqa: F405
                          electrodes, description, event_times, features)


if __name__ == '__main__':
    unittest.main()
