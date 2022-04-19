import warnings

import numpy as np

from pynwb.ecephys import ElectricalSeries, SpikeEventSeries, EventDetection, Clustering, EventWaveform,\
                          ClusterWaveforms, LFP, FilteredEphys, FeatureExtraction, ElectrodeGroup
from pynwb.device import Device
from pynwb.testing import TestCase

from hdmf.common import DynamicTableRegion

from pynwb.testing.mock.ecephys import mock_ElectricalSeries, mock_ElectrodeTable, mock_ElectrodeGroup, \
    mock_Device, mock_SpikeEventSeries


class ElectricalSeriesConstructor(TestCase):

    def test_init(self):
        data = np.ones((10, 5))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        filtering = 'Low-pass filter at 300 Hz'
        eS = mock_ElectricalSeries(
            name="test_eS",
            data=data,
            timestamps=ts,
            rate=None,
            filtering=filtering
        )
        self.assertEqual(eS.name, 'test_eS')
        np.testing.assert_array_equal(data, eS.data)
        self.assertEqual(eS.timestamps, ts)
        self.assertEqual(eS.filtering, filtering)

    def test_link(self):
        table = mock_ElectrodeTable()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        ts1 = ElectricalSeries('test_ts1', [0, 1, 2, 3, 4, 5], region, timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = ElectricalSeries('test_ts2', ts1, region, timestamps=ts1)
        ts3 = ElectricalSeries('test_ts3', ts2, region, timestamps=ts2)
        self.assertEqual(ts2.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts2.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.assertEqual(ts3.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts3.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def test_invalid_data_shape(self):
        with self.assertRaisesWith(ValueError, ("ElectricalSeries.__init__: incorrect shape for 'data' (got '(2, 2, 2, "
                                                "2)', expected '((None,), (None, None), (None, None, None))')")):
            mock_ElectricalSeries(data=np.ones((2, 2, 2, 2)))

    def test_dimensions_warning(self):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            mock_ElectricalSeries(data=np.ones((2, 6))),
            self.assertEqual(len(w), 1)
            assert (
                "The second dimension of data does not match the length of electrodes. Your data may be transposed."
                ) in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            mock_ElectricalSeries(
                data=np.ones((5, 10))
            )
            self.assertEqual(len(w), 1)
            assert (
               "The second dimension of data does not match the length of electrodes, but instead the first does. Data "
               "is oriented incorrectly and should be transposed."
                   ) in str(w[-1].message)


class SpikeEventSeriesConstructor(TestCase):

    def test_init(self):
        timestamps = np.arange(2)
        data = ((1, 1, 1), (2, 2, 2))
        sES = mock_SpikeEventSeries(
            name='test_sES',
            data=data,
            timestamps=timestamps,
        )
        self.assertEqual(sES.name, 'test_sES')
        np.testing.assert_array_equal(sES.data, data)
        np.testing.assert_array_equal(sES.timestamps, timestamps)

    def test_no_rate(self):

        with self.assertRaises(TypeError):
            mock_SpikeEventSeries(rate=1.)


class ElectrodeGroupConstructor(TestCase):

    def test_init(self):
        device = mock_Device()
        group = mock_ElectrodeGroup(
            name="elec1",
            description='electrode description',
            location='electrode location',
            device=device,
            position=(1, 2, 3),
        )
        self.assertEqual(group.name, 'elec1')
        self.assertEqual(group.description, 'electrode description')
        self.assertEqual(group.location, 'electrode location')
        self.assertEqual(group.device, device)
        self.assertEqual(group.position, (1, 2, 3))

    def test_init_position_none(self):
        dev1 = Device('dev1')
        group = ElectrodeGroup('elec1', 'electrode description', 'electrode location', dev1)
        self.assertEqual(group.name, 'elec1')
        self.assertEqual(group.description, 'electrode description')
        self.assertEqual(group.location, 'electrode location')
        self.assertEqual(group.device, dev1)
        self.assertIsNone(group.position)

    def test_init_position_bad(self):
        dev1 = Device('dev1')
        with self.assertRaises(TypeError):
            ElectrodeGroup('elec1', 'electrode description', 'electrode location', dev1, (1, 2))


class EventDetectionConstructor(TestCase):

    def test_event_detection(self):
        eS = mock_ElectricalSeries()
        eD = EventDetection('detection_method', eS, (1, 2, 3), (0.1, 0.2, 0.3))
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, (0.1, 0.2, 0.3))
        self.assertEqual(eD.unit, 'seconds')


class EventWaveformConstructor(TestCase):

    def test_init(self):
        table = mock_ElectrodeTable()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        sES = SpikeEventSeries('test_sES', list(range(10)), list(range(10)), region)

        ew = EventWaveform(sES)
        self.assertEqual(ew.spike_event_series['test_sES'], sES)
        self.assertEqual(ew['test_sES'], ew.spike_event_series['test_sES'])


class ClusteringConstructor(TestCase):

    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]

        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cc = Clustering('description', num, peak_over_rms, times)
        self.assertEqual(cc.description, 'description')
        self.assertEqual(cc.num, num)
        self.assertEqual(cc.peak_over_rms, peak_over_rms)
        self.assertEqual(cc.times, times)


class ClusterWaveformsConstructor(TestCase):

    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cc = Clustering('description', num, peak_over_rms, times)

        means = [[7.3, 7.3]]
        stdevs = [[8.3, 8.3]]

        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cw = ClusterWaveforms(cc, 'filtering', means, stdevs)
        self.assertEqual(cw.clustering_interface, cc)
        self.assertEqual(cw.waveform_filtering, 'filtering')
        self.assertEqual(cw.waveform_mean, means)
        self.assertEqual(cw.waveform_sd, stdevs)


class LFPTest(TestCase):

    def test_add_electrical_series(self):
        lfp = LFP()
        eS = mock_ElectricalSeries(name="test_eS")
        lfp.add_electrical_series(eS)
        self.assertEqual(lfp.electrical_series.get('test_eS'), eS)


class FilteredEphysTest(TestCase):

    def test_init(self):
        eS = mock_ElectricalSeries(name="test_eS")
        fe = FilteredEphys(eS)
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))

    def test_add_electrical_series(self):
        fe = FilteredEphys()
        eS = mock_ElectricalSeries(name="test_eS")
        fe.add_electrical_series(eS)
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))


class FeatureExtractionConstructor(TestCase):

    def test_init(self):
        event_times = [1.9, 3.5]
        table = mock_ElectrodeTable()
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]]
        fe = FeatureExtraction(region, description, event_times, features)
        self.assertEqual(fe.description, description)
        self.assertEqual(fe.times, event_times)
        self.assertEqual(fe.features, features)

    def test_invalid_init_mismatched_event_times(self):
        event_times = []  # Need 1 event time but give 0
        table = mock_ElectrodeTable()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, electrodes, description, event_times, features)

    def test_invalid_init_mismatched_electrodes(self):
        event_times = [1]
        table = mock_ElectrodeTable()
        electrodes = DynamicTableRegion('electrodes', [0], 'the first electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, electrodes, description, event_times, features)

    def test_invalid_init_mismatched_description(self):
        event_times = [1]
        table = mock_ElectrodeTable()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3', 'desc4']  # Need 3 descriptions but give 4
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, electrodes, description, event_times, features)

    def test_invalid_init_mismatched_description2(self):
        event_times = [1]
        table = mock_ElectrodeTable()
        electrodes = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[0, 1, 2], [3, 4, 5]]  # Need 3D feature array but give only 2D array
        self.assertRaises(ValueError, FeatureExtraction, electrodes, description, event_times, features)
