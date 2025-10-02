import numpy as np

from hdmf.common import VectorData, DynamicTableRegion

from pynwb.misc import (
    AnnotationSeries, AbstractFeatureSeries, IntervalSeries, Units, DecompositionSeries, FrequencyBandsTable
)
from pynwb.file import TimeSeries
from pynwb.device import Device
from pynwb.ecephys import ElectrodeGroup, ElectrodesTable
from pynwb.testing import TestCase


class AnnotationSeriesConstructor(TestCase):
    def test_init(self):
        aS = AnnotationSeries(name='test_aS', data=[1, 2, 3], timestamps=[1., 2., 3.])
        self.assertEqual(aS.name, 'test_aS')
        aS.add_annotation(2.0, 'comment')


class AbstractFeatureSeriesConstructor(TestCase):
    def test_init(self):
        aFS = AbstractFeatureSeries(name='test_aFS',
                                    feature_units=['feature units'],
                                    features=['features'],
                                    timestamps=list())
        self.assertEqual(aFS.name, 'test_aFS')
        self.assertEqual(aFS.feature_units, ['feature units'])
        self.assertEqual(aFS.features, ['features'])

        aFS.add_features(2.0, [1.])


class FrequencyBandsTableConstructor(TestCase):
    def setUp(self):
        self.bands = FrequencyBandsTable(
            columns=[
                VectorData(name='band_name', description='name of bands', data=['alpha', 'beta', 'gamma']),
                VectorData(name='band_limits', description='low and high cutoffs in Hz', data=np.ones((3, 2))),
                VectorData(name='band_mean', description='mean gaussian filters in Hz', data=np.ones((3,))),
                VectorData(
                    name='band_stdev',
                    description='standard deviation of gaussian filters in Hz',
                    data=np.ones((3,))
                ),
            ],
        )

    def test_init(self):
        self.assertEqual(self.bands['band_name'].data, ['alpha', 'beta', 'gamma'])
        np.testing.assert_equal(self.bands['band_limits'].data, np.ones((3, 2)))
        np.testing.assert_equal(self.bands['band_mean'].data, np.ones((3,)))
        np.testing.assert_equal(self.bands['band_stdev'].data, np.ones((3,)))

    def test_add_row(self):
        self.bands.add_band(band_name='band_name1', band_limits=np.array([1., 2.]), band_mean=1., band_stdev=1.)
        self.bands.add_band(band_name='band_name2', band_limits=(3., 4.), band_mean=1., band_stdev=1.)
        self.bands.add_band(band_name='band_name3', band_limits=[5., 6.], band_mean=1., band_stdev=1.)
        np.testing.assert_equal(
            self.bands['band_limits'].data,
            [[1., 1.], [1., 1.], [1., 1.], [1., 2.,], [3., 4.], [5., 6.]]
        )
        np.testing.assert_equal(self.bands['band_mean'].data, np.ones((6,)))
        np.testing.assert_equal(self.bands['band_stdev'].data, np.ones((6,)))


class DecompositionSeriesConstructor(TestCase):
    def test_init(self):
        timeseries = TimeSeries(name='dummy timeseries', description='desc',
                                data=np.ones((3, 3)), unit='Volts',
                                timestamps=[1., 2., 3.])
        bands = FrequencyBandsTable(
            columns=[
                VectorData(name='band_name', description='name of bands', data=['alpha', 'beta', 'gamma']),
                VectorData(name='band_limits', description='low and high cutoffs in Hz', data=np.ones((3, 2))),
                VectorData(name='band_mean', description='mean gaussian filters in Hz', data=np.ones((3,))),
                VectorData(
                    name='band_stdev',
                    description='standard deviation of gaussian filters in Hz',
                    data=np.ones((3,))
                ),
            ],
        )
        spec_anal = DecompositionSeries(name='LFPSpectralAnalysis',
                                        description='my description',
                                        data=np.ones((3, 3, 3)),
                                        timestamps=[1., 2., 3.],
                                        source_timeseries=timeseries,
                                        metric='amplitude',
                                        bands=bands)

        self.assertEqual(spec_anal.name, 'LFPSpectralAnalysis')
        self.assertEqual(spec_anal.description, 'my description')
        np.testing.assert_equal(spec_anal.data, np.ones((3, 3, 3)))
        np.testing.assert_equal(spec_anal.timestamps, [1., 2., 3.])
        self.assertEqual(spec_anal.bands['band_name'].data, ['alpha', 'beta', 'gamma'])
        np.testing.assert_equal(spec_anal.bands['band_limits'].data, np.ones((3, 2)))
        np.testing.assert_equal(spec_anal.bands['band_mean'].data, np.ones((3,)))
        np.testing.assert_equal(spec_anal.bands['band_stdev'].data, np.ones((3,)))
        self.assertEqual(spec_anal.source_timeseries, timeseries)
        self.assertEqual(spec_anal.metric, 'amplitude')

    def test_init_delayed_bands(self):
        timeseries = TimeSeries(name='dummy timeseries', description='desc',
                                data=np.ones((3, 3)), unit='Volts',
                                timestamps=np.ones((3,)))
        spec_anal = DecompositionSeries(name='LFPSpectralAnalysis',
                                        description='my description',
                                        data=np.ones((3, 3, 3)),
                                        timestamps=[1., 2., 3.],
                                        source_timeseries=timeseries,
                                        metric='amplitude')
        for band_name in ['alpha', 'beta', 'gamma']:
            spec_anal.add_band(band_name=band_name, band_limits=np.array([1., 1.]), band_mean=1., band_stdev=1.)
        self.assertEqual(spec_anal.name, 'LFPSpectralAnalysis')
        self.assertEqual(spec_anal.description, 'my description')
        np.testing.assert_equal(spec_anal.data, np.ones((3, 3, 3)))
        np.testing.assert_equal(spec_anal.timestamps, [1., 2., 3.])
        self.assertEqual(spec_anal.source_timeseries, timeseries)
        self.assertEqual(spec_anal.metric, 'amplitude')
        self.assertEqual(spec_anal.bands['band_name'].data, ['alpha', 'beta', 'gamma'])
        np.testing.assert_equal(spec_anal.bands['band_limits'].data, [np.array([1., 1.]) for _ in range(3)])

    @staticmethod
    def make_electrode_table(self):
        """ Make an electrode table, electrode group, and device """
        self.table = ElectrodesTable()
        self.dev1 = Device(name='dev1')
        self.group = ElectrodeGroup(name='tetrode1',
                                    description='tetrode description',
                                    location='tetrode location',
                                    device=self.dev1)
        for i in range(4):
            self.table.add_row(location='CA1', group=self.group, group_name='tetrode1')

    def test_init_with_source_channels(self):
        self.make_electrode_table(self)
        region = DynamicTableRegion(name='source_channels',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=self.table)
        data = np.random.randn(100, 2, 30)
        timestamps = np.arange(100)/100
        ds = DecompositionSeries(name='test_DS',
                                 data=data,
                                 source_channels=region,
                                 timestamps=timestamps,
                                 metric='amplitude')

        self.assertIs(ds.source_channels, region)


class IntervalSeriesConstructor(TestCase):
    def test_init(self):
        data = [1.0, -1.0, 1.0, -1.0]
        timestamps = [0.0, 1.0, 2.0, 3.0]
        iS = IntervalSeries(name='test_iS', data=data, timestamps=timestamps)
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.data, data)
        self.assertEqual(iS.timestamps, timestamps)

    def test_add_interval(self):
        data = [1.0, -1.0, 1.0, -1.0]
        timestamps = [0.0, 1.0, 2.0, 3.0]
        iS = IntervalSeries(name='test_iS', data=data, timestamps=timestamps)
        iS.add_interval(4.0, 5.0)
        data.append(1.0)
        data.append(-1.0)
        timestamps.append(4.0)
        timestamps.append(5.0)
        self.assertEqual(iS.data, data)
        self.assertEqual(iS.timestamps, timestamps)


class UnitsTests(TestCase):
    def test_init(self):
        ut = Units()
        self.assertEqual(ut.name, 'Units')
        self.assertFalse(ut.columns)

    def test_add_spike_times(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        self.assertEqual(ut.id.data, [0, 1])
        self.assertEqual(ut['spike_times'].target.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ut['spike_times'].data, [3, 6])
        self.assertEqual(ut['spike_times'][0], [0, 1, 2])
        self.assertEqual(ut['spike_times'][1], [3, 4, 5])

    def test_add_waveforms(self):
        ut = Units()
        wf1 = [
                [  # elec 1
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ], [  # elec 2
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ]
            ]
        wf2 = [
                [     # elec 1
                    [1, 2, 3],  # spike 1, [sample 1, sample 2, sample 3]
                    [1, 2, 3],  # spike 2
                    [1, 2, 3],  # spike 3
                    [1, 2, 3]   # spike 4
                ], [  # elec 2
                    [1, 2, 3],  # spike 1
                    [1, 2, 3],  # spike 2
                    [1, 2, 3],  # spike 3
                    [1, 2, 3]   # spike 4
                ], [  # elec 3
                    [1, 2, 3],  # spike 1
                    [1, 2, 3],  # spike 2
                    [1, 2, 3],  # spike 3
                    [1, 2, 3]   # spike 4
                ]
            ]
        ut.add_unit(waveforms=wf1)
        ut.add_unit(waveforms=wf2)
        self.assertEqual(ut.id.data, [0, 1])
        self.assertEqual(ut['waveforms'].target.data, [3, 6, 10, 14, 18])
        self.assertEqual(ut['waveforms'].data, [2, 5])
        self.assertListEqual(ut['waveforms'][0], wf1)
        self.assertListEqual(ut['waveforms'][1], wf2)

    def test_get_spike_times(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        self.assertTrue(all(ut.get_unit_spike_times(0) == np.array([0, 1, 2])))
        self.assertTrue(all(ut.get_unit_spike_times(1) == np.array([3, 4, 5])))

    @staticmethod
    def test_get_spike_times_interval():
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        np.testing.assert_array_equal(ut.get_unit_spike_times(0, (.5, 3)), [1, 2])
        np.testing.assert_array_equal(ut.get_unit_spike_times(0, (-.5, 1.1)), [0, 1])

    def test_get_spike_times_multi(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        np.testing.assert_array_equal(ut.get_unit_spike_times((0, 1)), [[0, 1, 2], [3, 4, 5]])

    def test_get_spike_times_multi_interval(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        np.testing.assert_array_equal(ut.get_unit_spike_times((0, 1), (1.5, 3.5)), [[2], [3]])

    def test_times(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2])
        ut.add_unit(spike_times=[3, 4, 5])
        self.assertTrue(all(ut['spike_times'][0] == np.array([0, 1, 2])))
        self.assertTrue(all(ut['spike_times'][1] == np.array([3, 4, 5])))

    def test_get_obs_intervals(self):
        ut = Units()
        ut.add_unit(obs_intervals=[[0, 1]])
        ut.add_unit(obs_intervals=[[2, 3], [4, 5]])
        self.assertTrue(np.all(ut.get_unit_obs_intervals(0) == np.array([[0, 1]])))
        self.assertTrue(np.all(ut.get_unit_obs_intervals(1) == np.array([[2, 3], [4, 5]])))

    def test_obs_intervals(self):
        ut = Units()
        ut.add_unit(obs_intervals=[[0, 1]])
        ut.add_unit(obs_intervals=[[2, 3], [4, 5]])
        self.assertTrue(np.all(ut['obs_intervals'][0] == np.array([[0, 1]])))
        self.assertTrue(np.all(ut['obs_intervals'][1] == np.array([[2, 3], [4, 5]])))

    def test_times_and_intervals(self):
        ut = Units()
        ut.add_unit(spike_times=[0, 1, 2], obs_intervals=[[0, 2]])
        ut.add_unit(spike_times=[3, 4, 5], obs_intervals=[[2, 3], [4, 5]])
        self.assertTrue(all(ut['spike_times'][0] == np.array([0, 1, 2])))
        self.assertTrue(all(ut['spike_times'][1] == np.array([3, 4, 5])))
        self.assertTrue(np.all(ut['obs_intervals'][0] == np.array([[0, 2]])))
        self.assertTrue(np.all(ut['obs_intervals'][1] == np.array([[2, 3], [4, 5]])))

    def test_electrode_group(self):
        ut = Units()
        device = Device(name='test_device')
        electrode_group = ElectrodeGroup(name='test_electrode_group',
                                         description='description',
                                         location='location',
                                         device=device)
        ut.add_unit(electrode_group=electrode_group)
        self.assertEqual(ut['electrode_group'][0], electrode_group)

    def test_waveform_attrs(self):
        ut = Units(waveform_rate=40000.)
        self.assertEqual(ut.waveform_rate, 40000.)
        self.assertEqual(ut.waveform_unit, 'volts')
