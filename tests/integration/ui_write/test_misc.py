import numpy as np

from hdmf.common import DynamicTable, VectorData
from pynwb import TimeSeries
from pynwb.misc import Units, DecompositionSeries
from pynwb.testing import TestMapRoundTrip, TestDataInterfaceIO


class TestUnitsIO(TestDataInterfaceIO):

    def setUpContainer(self):
        ut = Units(name='UnitsTest', description='a simple table for testing Units')
        ut.add_unit(spike_times=[0, 1, 2], obs_intervals=[[0, 1], [2, 3]])
        ut.add_unit(spike_times=[3, 4, 5], obs_intervals=[[2, 5], [6, 7]])
        return ut

    def test_get_spike_times(self):
        ut = self.roundtripContainer()
        received = ut.get_unit_spike_times(0)
        self.assertTrue(np.array_equal(received, [0, 1, 2]))
        received = ut.get_unit_spike_times(1)
        self.assertTrue(np.array_equal(received, [3, 4, 5]))
        self.assertTrue(np.array_equal(ut['spike_times'][:], [[0, 1, 2], [3, 4, 5]]))

    def test_get_obs_intervals(self):
        ut = self.roundtripContainer()
        received = ut.get_unit_obs_intervals(0)
        self.assertTrue(np.array_equal(received, [[0, 1], [2, 3]]))
        received = ut.get_unit_obs_intervals(1)
        self.assertTrue(np.array_equal(received, [[2, 5], [6, 7]]))
        self.assertTrue(np.array_equal(ut['obs_intervals'][:], [[[0, 1], [2, 3]], [[2, 5], [6, 7]]]))


class TestUnitElectrodes(TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return Units('placeholder_units')

    def addContainer(self, nwbfile):
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
                                  x=1.0, y=2.0, z=3.0,
                                  imp=float(-idx),
                                  location='CA1', filtering='none',
                                  group=electrode_group)

        nwbfile.add_unit(id=1, electrodes=[1], electrode_group=electrode_group)
        nwbfile.add_unit(id=2, electrodes=[1], electrode_group=electrode_group)
        nwbfile.units.to_dataframe()
        self.container = nwbfile.units

    def getContainer(self, nwbfile):
        return nwbfile.units


class TestSpectralAnalysis(TestDataInterfaceIO):

    def setUpContainer(self):
        self.timeseries = TimeSeries(name='dummy timeseries', description='desc',
                                     data=np.ones((3, 3)), unit='flibs',
                                     timestamps=np.ones((3,)))
        bands = DynamicTable(name='bands', description='band info for LFPSpectralAnalysis', columns=[
            VectorData(name='band_name', description='name of bands', data=['alpha', 'beta', 'gamma']),
            VectorData(name='band_limits', description='low and high cutoffs in Hz', data=np.ones((3, 2)))
        ])
        spec_anal = DecompositionSeries(name='LFPSpectralAnalysis',
                                        description='my description',
                                        data=np.ones((3, 3, 3)),
                                        timestamps=np.ones((3,)),
                                        source_timeseries=self.timeseries,
                                        metric='amplitude',
                                        bands=bands)

        return spec_anal

    def addContainer(self, nwbfile):
        nwbfile.add_acquisition(self.timeseries)
        prcs_mod = nwbfile.create_processing_module('test_mod', 'test_mod')
        prcs_mod.add(self.container)

    def getContainer(self, nwbfile):
        return nwbfile.processing['test_mod']['LFPSpectralAnalysis']
