import warnings

import numpy as np

from pynwb.base import ProcessingModule
from pynwb.ecephys import (
    ElectricalSeries,
    SpikeEventSeries,
    EventDetection,
    Clustering,
    EventWaveform,
    ClusterWaveforms,
    LFP,
    FilteredEphys,
    FeatureExtraction,
    ElectrodeGroup,
)
from pynwb.device import Device
from pynwb.file import ElectrodeTable
from pynwb.testing import TestCase
from pynwb.testing.mock.ecephys import mock_ElectricalSeries

from hdmf.common import DynamicTableRegion


def make_electrode_table():
    table = ElectrodeTable()
    dev1 = Device('dev1')
    group = ElectrodeGroup('tetrode1', 'tetrode description', 'tetrode location', dev1)
    table.add_row(location='CA1', group=group, group_name='tetrode1')
    table.add_row(location='CA1', group=group, group_name='tetrode1')
    table.add_row(location='CA1', group=group, group_name='tetrode1')
    table.add_row(location='CA1', group=group, group_name='tetrode1')

    return table


class ElectricalSeriesConstructor(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        channel_conversion = [2., 6.3]
        filtering = 'Low-pass filter at 300 Hz'
        table, region = self._create_table_and_region()
        eS = ElectricalSeries(
            name='test_eS',
            data=data,
            electrodes=region,
            channel_conversion=channel_conversion,
            filtering=filtering,
            timestamps=ts
        )
        self.assertEqual(eS.name, 'test_eS')
        self.assertEqual(eS.data, data)
        self.assertEqual(eS.electrodes, region)
        self.assertEqual(eS.timestamps, ts)
        self.assertEqual(eS.channel_conversion, [2., 6.3])
        self.assertEqual(eS.filtering, filtering)

    def test_link(self):
        table, region = self._create_table_and_region()
        ts1 = ElectricalSeries('test_ts1', [0, 1, 2, 3, 4, 5], region, timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = ElectricalSeries('test_ts2', ts1, region, timestamps=ts1)
        ts3 = ElectricalSeries('test_ts3', ts2, region, timestamps=ts2)
        self.assertEqual(ts2.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts2.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.assertEqual(ts3.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts3.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def test_invalid_data_shape(self):
        table, region = self._create_table_and_region()
        with self.assertRaisesWith(ValueError, ("ElectricalSeries.__init__: incorrect shape for 'data' (got '(2, 2, 2, "
                                                "2)', expected '((None,), (None, None), (None, None, None))')")):
            ElectricalSeries('test_ts1', np.ones((2, 2, 2, 2)), region, timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def test_dimensions_warning(self):
        table, region = self._create_table_and_region()
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            ElectricalSeries(
                name="test_ts1",
                data=np.ones((6, 3)),
                electrodes=region,
                timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
            )
            self.assertEqual(len(w), 1)
            assert (
                "ElectricalSeries 'test_ts1': The second dimension of data does not match the length of electrodes. "
                "Your data may be transposed."
                ) in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            ElectricalSeries(
                name="test_ts1",
                data=np.ones((2, 6)),
                electrodes=region,
                rate=30000.,
            )
            self.assertEqual(len(w), 1)
            assert (
               "ElectricalSeries 'test_ts1': The second dimension of data does not match the length of electrodes, "
               "but instead the first does. Data is oriented incorrectly and should be transposed."
                   ) in str(w[-1].message)

    def test_get_data_in_units(self):
        samples = 100
        channels = 5
        conversion = 10.0
        offset = 3.0
        channel_conversion = np.random.rand(channels)

        electrical_series = mock_ElectricalSeries(
            data=np.ones((samples, channels)),
            conversion=conversion,
            offset=offset,
            channel_conversion=channel_conversion,
        )

        data_in_units = electrical_series.get_data_in_units()

        for channel_index in range(channels):
            np.testing.assert_almost_equal(
                data_in_units[:, channel_index],
                np.ones(samples) * conversion * channel_conversion[channel_index] + offset
            )


class SpikeEventSeriesConstructor(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[1, 3],
            description='the second and fourth electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        table, region = self._create_table_and_region()
        data = ((1, 1), (2, 2), (3, 3))
        timestamps = np.arange(3)
        sES = SpikeEventSeries(name='test_sES', data=data, timestamps=timestamps, electrodes=region)
        self.assertEqual(sES.name, 'test_sES')
        # self.assertListEqual(sES.data, data)
        np.testing.assert_array_equal(sES.data, data)
        np.testing.assert_array_equal(sES.timestamps, timestamps)

    def test_no_rate(self):
        table, region = self._create_table_and_region()
        data = ((1, 1, 1), (2, 2, 2))
        with self.assertRaises(TypeError):
            SpikeEventSeries(name='test_sES', data=data, electrodes=region, rate=1.)

    def test_incorrect_timestamps(self):
        table, region = self._create_table_and_region()
        data = ((1, 1, 1), (2, 2, 2))
        with self.assertRaisesWith(ValueError, "Must provide the same number of timestamps and spike events"):
            SpikeEventSeries(name='test_sES', data=data, electrodes=region, timestamps=[1.0, 2.0, 3.0])


class ElectrodeGroupConstructor(TestCase):

    def test_init(self):
        dev1 = Device('dev1')
        group = ElectrodeGroup('elec1', 'electrode description', 'electrode location', dev1, (1, 2, 3))
        self.assertEqual(group.name, 'elec1')
        self.assertEqual(group.description, 'electrode description')
        self.assertEqual(group.location, 'electrode location')
        self.assertEqual(group.device, dev1)
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
        with self.assertRaises(ValueError):
            ElectrodeGroup('elec1', 'electrode description', 'electrode location', dev1, (1, 2))


class EventDetectionConstructor(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        table, region = self._create_table_and_region()
        eS = ElectricalSeries('test_eS', data, region, timestamps=ts)
        eD = EventDetection('detection_method', eS, (1, 2, 3), (0.1, 0.2, 0.3))
        self.assertEqual(eD.detection_method, 'detection_method')
        self.assertEqual(eD.source_electricalseries, eS)
        self.assertEqual(eD.source_idx, (1, 2, 3))
        self.assertEqual(eD.times, (0.1, 0.2, 0.3))
        self.assertEqual(eD.unit, 'seconds')


class EventWaveformConstructor(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        table, region = self._create_table_and_region()
        sES = SpikeEventSeries('test_sES', list(range(10)), list(range(10)), region)

        pm = ProcessingModule(name='test_module', description='a test module')
        ew = EventWaveform()
        pm.add(table)
        pm.add(ew)
        ew.add_spike_event_series(sES)
        self.assertEqual(ew.spike_event_series['test_sES'], sES)
        self.assertEqual(ew['test_sES'], ew.spike_event_series['test_sES'])


class ClusteringConstructor(TestCase):

    def test_init(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]

        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cc = Clustering(description='description', num=num, peak_over_rms=peak_over_rms, times=times)
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
            cc = Clustering(description='description', num=num, peak_over_rms=peak_over_rms, times=times)

        means = [[7.3, 7.3]]
        stdevs = [[8.3, 8.3]]

        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cw = ClusterWaveforms(
                clustering_interface=cc,
                waveform_filtering='filtering',
                waveform_mean=means,
                waveform_sd=stdevs
            )
        self.assertEqual(cw.clustering_interface, cc)
        self.assertEqual(cw.waveform_filtering, 'filtering')
        self.assertEqual(cw.waveform_mean, means)
        self.assertEqual(cw.waveform_sd, stdevs)


class LFPTest(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        _, region = self._create_table_and_region()
        eS = ElectricalSeries('test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        msg = (
            "The linked table for DynamicTableRegion 'electrodes' does not share "
            "an ancestor with the DynamicTableRegion."
        )
        with self.assertWarnsRegex(UserWarning, msg):
            lfp = LFP(eS)
        self.assertEqual(lfp.electrical_series.get('test_eS'), eS)
        self.assertEqual(lfp['test_eS'], lfp.electrical_series.get('test_eS'))

    def test_add_electrical_series(self):
        lfp = LFP()
        table, region = self._create_table_and_region()
        eS = ElectricalSeries('test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        pm = ProcessingModule(name='test_module', description='a test module')
        pm.add(table)
        pm.add(lfp)
        lfp.add_electrical_series(eS)
        self.assertEqual(lfp.electrical_series.get('test_eS'), eS)


class FilteredEphysTest(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        _, region = self._create_table_and_region()
        eS = ElectricalSeries('test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        msg = (
            "The linked table for DynamicTableRegion 'electrodes' does not share "
            "an ancestor with the DynamicTableRegion."
        )
        with self.assertWarnsRegex(UserWarning, msg):
            fe = FilteredEphys(eS)
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))

    def test_add_electrical_series(self):
        table, region = self._create_table_and_region()
        eS = ElectricalSeries('test_eS', [0, 1, 2, 3], region, timestamps=[0.1, 0.2, 0.3, 0.4])
        pm = ProcessingModule(name='test_module', description='a test module')
        fe = FilteredEphys()
        pm.add(table)
        pm.add(fe)
        fe.add_electrical_series(eS)
        self.assertEqual(fe.electrical_series.get('test_eS'), eS)
        self.assertEqual(fe['test_eS'], fe.electrical_series.get('test_eS'))


class FeatureExtractionConstructor(TestCase):

    def _create_table_and_region(self):
        table = make_electrode_table()
        region = DynamicTableRegion(
            name='electrodes',
            data=[0, 2],
            description='the first and third electrodes',
            table=table
        )
        return table, region

    def test_init(self):
        event_times = [1.9, 3.5]
        table, region = self._create_table_and_region()
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]]
        fe = FeatureExtraction(region, description, event_times, features)
        self.assertEqual(fe.description, description)
        self.assertEqual(fe.times, event_times)
        self.assertEqual(fe.features, features)

    def test_invalid_init_mismatched_event_times(self):
        event_times = []  # Need 1 event time but give 0
        table, region = self._create_table_and_region()
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, region, description, event_times, features)

    def test_invalid_init_mismatched_electrodes(self):
        event_times = [1]
        table = make_electrode_table()
        region = DynamicTableRegion(name='electrodes', data=[0], description='the first electrode', table=table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, region, description, event_times, features)

    def test_invalid_init_mismatched_description(self):
        event_times = [1]
        table, region = self._create_table_and_region()
        description = ['desc1', 'desc2', 'desc3', 'desc4']  # Need 3 descriptions but give 4
        features = [[[0, 1, 2], [3, 4, 5]]]
        self.assertRaises(ValueError, FeatureExtraction, region, description, event_times, features)

    def test_invalid_init_mismatched_description2(self):
        event_times = [1]
        table, region = self._create_table_and_region()
        description = ['desc1', 'desc2', 'desc3']
        features = [[0, 1, 2], [3, 4, 5]]  # Need 3D feature array but give only 2D array
        self.assertRaises(ValueError, FeatureExtraction, region, description, event_times, features)
