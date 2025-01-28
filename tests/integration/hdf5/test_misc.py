import numpy as np

from hdmf.common import DynamicTable, VectorData, DynamicTableRegion
from pynwb import TimeSeries
from pynwb.misc import Units, DecompositionSeries
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase
from pynwb.ecephys import ElectrodeGroup
from pynwb.device import Device
from pynwb.file import ElectrodeTable as get_electrode_table


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


class TestUnitsFileIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return placeholder Units object. Tested units are added directly to the NWBFile in addContainer """
        return Units('placeholder')  # this will get ignored

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
        bands = DynamicTable(
            name='bands',
            description='band info for LFPSpectralAnalysis',
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
        self.table = get_electrode_table()
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
        bands = DynamicTable(
            name='bands',
            description='band info for LFPSpectralAnalysis',
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
