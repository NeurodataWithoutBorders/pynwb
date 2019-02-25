from . import base

import numpy as np
from pynwb.form.build import GroupBuilder, DatasetBuilder, ReferenceBuilder
from pynwb import TimeSeries
from pynwb.core import DynamicTable, VectorData

from pynwb.misc import Units, DecompositionSeries


class TestUnitsIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        ut = Units(name='UnitsTest', description='a simple table for testing Units')
        ut.add_unit(spike_times=[0, 1, 2], obs_intervals=[[0, 1], [2, 3]])
        ut.add_unit(spike_times=[3, 4, 5], obs_intervals=[[2, 5], [6, 7]])
        return ut

    def setUpBuilder(self):
        ids_builder = DatasetBuilder('id', [0, 1],
                                     attributes={'neurodata_type': 'ElementIdentifiers',
                                                 'namespace': 'core',
                                                 'help': 'unique identifiers for a list of elements'})
        st_builder = DatasetBuilder('spike_times', [0, 1, 2, 3, 4, 5],
                                    attributes={'neurodata_type': 'VectorData',
                                                'namespace': 'core',
                                                'description': 'the spike times for each unit',
                                                'help': 'Values for a list of elements'})
        sti_builder = DatasetBuilder('spike_times_index',
                                     [3, 6],
                                     attributes={'neurodata_type': 'VectorIndex',
                                                 'namespace': 'core',
                                                 'target': ReferenceBuilder(st_builder),
                                                 'help': 'indexes into a list of values for a list of elements'})

        obs_builder = DatasetBuilder('obs_intervals', [[0, 1], [2, 3], [2, 5], [6, 7]],
                                     attributes={'neurodata_type': 'VectorData',
                                                 'namespace': 'core',
                                                 'description': 'the observation intervals for each unit',
                                                 'help': 'Values for a list of elements'})

        obsi_builder = DatasetBuilder('obs_intervals_index',
                                      [2, 4],
                                      attributes={'neurodata_type': 'VectorIndex',
                                                  'namespace': 'core',
                                                  'target': ReferenceBuilder(obs_builder),
                                                  'help': 'indexes into a list of values for a list of elements'})

        return GroupBuilder('UnitsTest',
                            attributes={'neurodata_type': 'Units',
                                        'namespace': 'core',
                                        'help': 'Data about spiking units',
                                        'description': 'a simple table for testing Units',
                                        'colnames': (b'spike_times', b'obs_intervals',)},
                            datasets={'id': ids_builder,
                                      'spike_times': st_builder,
                                      'spike_times_index': sti_builder,
                                      'obs_intervals': obs_builder,
                                      'obs_intervals_index': obsi_builder})

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


class TestUnitElectrodes(base.TestMapRoundTrip):

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
            nwbfile.add_electrode(idx,
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


class TestSpectralAnalysis(base.TestDataInterfaceIO):
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
        prcs_mod.add_data_interface(self.container)

    def getContainer(self, nwbfile):

        return nwbfile.modules['test_mod']['LFPSpectralAnalysis']
