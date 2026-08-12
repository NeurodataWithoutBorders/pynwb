import h5py
import numpy as np

from hdmf.common import VectorData, DynamicTableRegion
from pynwb import NWBHDF5IO, TimeSeries
from pynwb.misc import Units, DecompositionSeries, FrequencyBandsTable
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase, remove_test_file
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.ecephys import ElectrodeGroup, ElectrodesTable
from pynwb.device import Device


class TestUnitsIO(AcquisitionH5IOMixin, TestCase):
    """ Test adding Units into acquisition and accessing Units after read """

    def setUpContainer(self):
        """ Return the test Units to read/write """
        ut = Units(name='UnitsTest', description='a simple table for testing Units')
        ut.add_unit(spike_times=[0., 1., 2.], obs_intervals=[[0., 1.], [2., 3.]],
                    waveform_mean=[1., 2., 3.], waveform_sd=[4., 5., 6.],
                    waveforms=[
                        [  # elec 1
                            [1, 2, 3],
                            [1, 2, 3],
                            [1, 2, 3]
                        ], [  # elec 2
                            [1, 2, 3],
                            [1, 2, 3],
                            [1, 2, 3]
                        ]
                    ])
        ut.add_unit(spike_times=[3., 4., 5.], obs_intervals=[[2., 5.], [6., 7.]],
                    waveform_mean=[1., 2., 3.], waveform_sd=[4., 5., 6.],
                    waveforms=np.array([
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
                    ]))
        ut.waveform_rate = 40000.
        ut.resolution = 1/40000
        return ut

    def test_get_spike_times(self):
        """ Test whether the Units spike times read from file are what was written """
        ut = self.roundtripContainer()
        received = ut.get_unit_spike_times(0)
        np.testing.assert_array_equal(received, [0., 1., 2.])
        received = ut.get_unit_spike_times(1)
        np.testing.assert_array_equal(received, [3., 4., 5.])
        np.testing.assert_array_equal(ut['spike_times'][:], [[0., 1., 2.], [3., 4., 5.]])

    def test_get_obs_intervals(self):
        """ Test whether the Units observation intervals read from file are what was written """
        ut = self.roundtripContainer()
        received = ut.get_unit_obs_intervals(0)
        np.testing.assert_array_equal(received, [[0., 1.], [2., 3.]])
        received = ut.get_unit_obs_intervals(1)
        np.testing.assert_array_equal(received, [[2., 5.], [6., 7.]])
        np.testing.assert_array_equal(ut['obs_intervals'][:], [[[0., 1.], [2., 3.]], [[2., 5.], [6., 7.]]])


class TestUnitsWaveformsOnlyIO(AcquisitionH5IOMixin, TestCase):
    """Test roundtripping waveform metadata when only waveforms are present."""

    def setUpContainer(self):
        ut = Units(name='UnitsWaveformsOnlyTest', description='a simple table for testing Units waveforms')
        ut.add_unit(
            spike_times=[0., 1., 2.],
            waveforms=[
                [
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ], [
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ]
            ]
        )
        ut.add_unit(
            spike_times=[3., 4., 5.],
            waveforms=np.array([
                [
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ], [
                    [1, 2, 3],
                    [1, 2, 3],
                    [1, 2, 3]
                ]
            ])
        )
        ut.waveform_rate = 40000.
        return ut

    def test_waveform_metadata_roundtrip(self):
        ut = self.roundtripContainer()
        self.assertEqual(ut.waveform_rate, 40000.)
        self.assertEqual(ut.waveform_unit, 'volts')

    def test_waveforms_attributes_written(self):
        self.roundtripContainer()
        with h5py.File(self.filename, 'r') as infile:
            waveforms = infile['acquisition'][self.container.name]['waveforms']
            self.assertEqual(waveforms.attrs['sampling_rate'], 40000.)
            unit = waveforms.attrs['unit']
            if isinstance(unit, bytes):
                unit = unit.decode('utf-8')
            self.assertEqual(unit, 'volts')


class TestUnitsCustomWaveformUnitIO(AcquisitionH5IOMixin, TestCase):
    """Test roundtripping a waveform unit other than the default 'volts'."""

    def setUpContainer(self):
        ut = Units(
            name='UnitsCustomWaveformUnitTest',
            description='a simple table for testing a custom Units waveform unit',
            waveform_rate=40000.,
            waveform_unit='microvolts',
        )
        ut.add_unit(
            spike_times=[0., 1., 2.],
            waveform_mean=[1., 2., 3.],
            waveform_sd=[4., 5., 6.],
            waveforms=[
                [  # elec 1
                    [1, 2, 3],
                    [1, 2, 3]
                ], [  # elec 2
                    [1, 2, 3],
                    [1, 2, 3]
                ]
            ],
        )
        return ut

    def test_waveform_unit_roundtrip(self):
        ut = self.roundtripContainer()
        self.assertEqual(ut.waveform_unit, 'microvolts')

    def test_waveform_unit_written(self):
        self.roundtripContainer()
        with h5py.File(self.filename, 'r') as infile:
            units = infile['acquisition'][self.container.name]
            for column in ('waveform_mean', 'waveform_sd', 'waveforms'):
                unit = units[column].attrs['unit']
                if isinstance(unit, bytes):
                    unit = unit.decode('utf-8')
                self.assertEqual(unit, 'microvolts')


class TestUnitsWaveformTimeBeforePeakIO(AcquisitionH5IOMixin, TestCase):
    """Test roundtripping the time from the start of a waveform to the spike peak."""

    def setUpContainer(self):
        ut = Units(
            name='UnitsWaveformTimeBeforePeakTest',
            description='a simple table for testing the Units waveform peak alignment',
            waveform_rate=40000.,
            waveform_time_before_peak_in_ms=1.5,
        )
        ut.add_unit(
            spike_times=[0., 1., 2.],
            waveform_mean=[1., 2., 3.],
            waveform_sd=[4., 5., 6.],
            waveforms=[
                [  # elec 1
                    [1, 2, 3],
                    [1, 2, 3]
                ], [  # elec 2
                    [1, 2, 3],
                    [1, 2, 3]
                ]
            ],
        )
        return ut

    def test_waveform_time_before_peak_roundtrip(self):
        ut = self.roundtripContainer()
        self.assertEqual(ut.waveform_time_before_peak_in_ms, 1.5)

    def test_waveform_time_before_peak_written(self):
        self.roundtripContainer()
        with h5py.File(self.filename, 'r') as infile:
            units = infile['acquisition'][self.container.name]
            for column in ('waveform_mean', 'waveform_sd', 'waveforms'):
                self.assertEqual(units[column].attrs['time_before_peak_in_ms'], 1.5)


class TestUnitsWaveformTimeBeforePeakOmitted(TestCase):
    """Test a Units table whose waveform peak alignment is unset."""

    def setUp(self):
        self.filename = 'test_units_waveform_time_before_peak_omitted.nwb'
        nwbfile = mock_NWBFile()
        ut = Units(name='units', description='a table without waveform peak alignment')
        ut.add_unit(spike_times=[0., 1., 2.], waveform_mean=[1., 2., 3.])
        nwbfile.units = ut
        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(nwbfile)

    def tearDown(self):
        remove_test_file(self.filename)

    def test_attribute_not_written(self):
        with h5py.File(self.filename, 'r') as infile:
            self.assertNotIn('time_before_peak_in_ms', infile['units']['waveform_mean'].attrs)

    def test_read_as_none(self):
        with NWBHDF5IO(self.filename, 'r') as io:
            nwbfile = io.read()
            self.assertIsNone(nwbfile.units.waveform_time_before_peak_in_ms)


class TestUnitsMismatchedWaveformUnit(TestCase):
    """Test reading a file whose waveform columns carry different unit attributes."""

    def setUp(self):
        self.filename = 'test_units_mismatched_waveform_unit.nwb'
        nwbfile = mock_NWBFile()
        ut = Units(name='units', description='a table for testing mismatched waveform units')
        ut.add_unit(
            spike_times=[0., 1., 2.],
            waveform_mean=[1., 2., 3.],
            waveform_sd=[4., 5., 6.],
        )
        nwbfile.units = ut
        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(nwbfile)
        with h5py.File(self.filename, 'r+') as infile:
            infile['units']['waveform_sd'].attrs['unit'] = 'microvolts'

    def tearDown(self):
        remove_test_file(self.filename)

    def test_warn_on_mismatched_unit(self):
        msg = ("The 'unit' attribute differs across the waveform columns of Units 'units': "
               "{'waveform_mean': 'volts', 'waveform_sd': 'microvolts'}. Using the value of 'waveform_mean'.")
        with self.assertWarnsWith(UserWarning, msg):
            with NWBHDF5IO(self.filename, 'r') as io:
                nwbfile = io.read()
                self.assertEqual(nwbfile.units.waveform_unit, 'volts')


class TestUnitsFileIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return placeholder Units object. Tested units are added directly to the NWBFile in addContainer """
        return Units(name='placeholder')  # this will get ignored

    def addContainer(self, nwbfile):
        """ Add units to the given NWBFile """
        device = nwbfile.create_device(name='trodes_rig123')
        electrode_name = 'tetrode1'
        description = "an example tetrode"
        location = "somewhere in the hippocampus"
        electrode_group = nwbfile.create_electrode_group(electrode_name,
                                                         description=description,
                                                         location=location,
                                                         device=device)
        for idx in [1, 2, 3, 4]:
            nwbfile.add_electrode(id=idx,
                                  location='CA1',
                                  group=electrode_group)

        nwbfile.add_unit(id=1, electrodes=[1], electrode_group=electrode_group)
        nwbfile.add_unit(id=2, electrodes=[1], electrode_group=electrode_group)
        self.container = nwbfile.units  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test Units from the given NWBFile """
        return nwbfile.units

    def test_to_dataframe(self):
        units = self.roundtripContainer()
        units.to_dataframe()


class TestDecompositionSeriesIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test DecompositionSeries to read/write """
        self.timeseries = TimeSeries(
            name='dummy timeseries',
            description='desc',
            data=np.ones((3, 3)),
            unit='flibs',
            timestamps=np.ones((3,)),
        )
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
        spec_anal = DecompositionSeries(
            name='LFPSpectralAnalysis',
            description='my description',
            data=np.ones((3, 3, 3)),
            timestamps=np.ones((3,)),
            source_timeseries=self.timeseries,
            metric='amplitude',
            bands=bands,
        )

        return spec_anal

    def addContainer(self, nwbfile):
        """ Add the test DecompositionSeries to the given NWBFile in a processing module """
        nwbfile.add_acquisition(self.timeseries)
        prcs_mod = nwbfile.create_processing_module('test_mod', 'test_mod')
        prcs_mod.add(self.container)

    def getContainer(self, nwbfile):
        """ Return the test DecompositionSeries from the given NWBFile """
        return nwbfile.processing['test_mod']['LFPSpectralAnalysis']


class TestDecompositionSeriesWithSourceChannelsIO(AcquisitionH5IOMixin, TestCase):

    @staticmethod
    def make_electrode_table(self):
        """ Make an electrode table, electrode group, and device """
        self.table = ElectrodesTable()
        self.dev1 = Device(name='dev1')
        self.group = ElectrodeGroup(
            name='tetrode1',
            description='tetrode description',
            location='tetrode location',
            device=self.dev1
        )
        for _ in range(4):
            self.table.add_row(location='CA1', group=self.group, group_name='tetrode1')

    def setUpContainer(self):
        """ Return the test ElectricalSeries to read/write """
        self.make_electrode_table(self)
        region = DynamicTableRegion(
            name='source_channels',
            data=[0, 2],
            description='the first and third electrodes',
            table=self.table
        )
        data = np.random.randn(100, 2, 30)
        timestamps = np.arange(100)/100
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
        ds = DecompositionSeries(
            name='test_DS',
            data=data,
            source_channels=region,
            timestamps=timestamps,
            metric='amplitude',
            bands=bands,
        )
        return ds

    def addContainer(self, nwbfile):
        """ Add the test ElectricalSeries and related objects to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def test_eg_ref(self):
        """
        Test that the electrode DynamicTableRegion references of the read ElectricalSeries have a group that
        correctly resolves to ElectrodeGroup instances.
        """
        read = self.roundtripContainer()
        row1 = read.source_channels[0]
        row2 = read.source_channels[1]
        self.assertIsInstance(row1.iloc[0]['group'], ElectrodeGroup)
        self.assertIsInstance(row2.iloc[0]['group'], ElectrodeGroup)
