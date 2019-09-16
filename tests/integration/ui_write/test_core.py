from pynwb.core import DynamicTable
import pynwb

from . import base

import pandas as pd
import numpy as np


class TestTrials(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('trials', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.add_trial_column('foo', 'an int column')
        nwbfile.add_trial_column('bar', 'a float column')
        nwbfile.add_trial_column('baz', 'a string column')
        nwbfile.add_trial_column('qux', 'a boolean column')
        nwbfile.add_trial(start_time=0., stop_time=1., foo=27, bar=28.0, baz="29", qux=True)
        nwbfile.add_trial(start_time=2., stop_time=3., foo=37, bar=38.0, baz="39", qux=False)
        # reset the thing
        self.container = nwbfile.trials

    def getContainer(self, nwbfile):
        return nwbfile.trials

    def actOnContainer(self, nwbfile):
        nwbfile.add_trial(start_time=0., stop_time=1., foo=27, bar=28.0, baz="29", qux=True)


class TestInvalidTimeInterval(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('invalid_times', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.add_invalid_time_interval(start_time=1.0, stop_time=2.0)
        nwbfile.add_invalid_time_interval(start_time=5.0, stop_time=7.0)
        # reset the thing
        self.container = nwbfile.invalid_times

    def getContainer(self, nwbfile):
        return nwbfile.invalid_times

    def actOnContainer(self, nwbfile):
        nwbfile.add_invalid_time_interval(start_time=8.0, stop_time=12.7)


class TestUnits(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('units', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.add_unit_column('foo', 'an int column')
        nwbfile.add_unit_column('my_bool', 'a bool column')
        nwbfile.add_unit(foo=27, my_bool=True)
        nwbfile.add_unit(foo=37, my_bool=False)
        # reset the thing
        self.container = nwbfile.units

    def getContainer(self, nwbfile):
        return nwbfile.units

    def actOnContainer(self, nwbfile):
        nwbfile.add_unit(foo=100, my_bool=False)


class TestFromDataframe(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable.from_dataframe(pd.DataFrame({
                'a': [[1, 2, 3],
                      [1, 2, 3],
                      [1, 2, 3]],
                'b': ['4', '5', '6']
            }), 'test_table')

    def addContainer(self, nwbfile):
        test_mod = nwbfile.create_processing_module('test', 'desc')
        test_mod.add(self.container)

    def getContainer(self, nwbfile):
        dyn_tab = nwbfile.processing['test'].data_interfaces['test_table']
        dyn_tab.to_dataframe()  # also test 2D column round-trip
        return dyn_tab


class TestElectrodes(base.TestMapRoundTrip):

    def setUpContainer(self):
        return DynamicTable('electrodes', 'metadata about extracellular electrodes')

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        self.dev1 = nwbfile.create_device('dev1')
        self.group = nwbfile.create_electrode_group('tetrode1', 'tetrode description', 'tetrode location', self.dev1)

        nwbfile.add_electrode(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        self.container = nwbfile.electrodes

    def getContainer(self, nwbfile):
        return nwbfile.electrodes

    def test_roundtrip(self):
        super(TestElectrodes, self).test_roundtrip()
        self.assertContainerEqual(self.read_container[0][7], self.container[0][7])

    def actOnContainer(self, nwbfile):
        nwbfile.add_electrode(id=5, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')


class TestElectrodesRegion(base.TestMapRoundTrip):

    def setUpContainer(self):
        return DynamicTable('electrodes', 'metadata about extracellular electrodes')  # no-op

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        self.dev1 = nwbfile.create_device('dev1')
        self.group = nwbfile.create_electrode_group('tetrode1', 'tetrode description', 'tetrode location', self.dev1)

        nwbfile.add_electrode(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')

        region = nwbfile.create_electrode_table_region(
            region=tuple([1, 2, 3]),
            name='electrodes',
            description='desc'
        )
        nwbfile.add_acquisition(pynwb.ecephys.ElectricalSeries(
            name='test_data',
            data=np.arange(10),
            timestamps=np.arange(10),
            electrodes=region
        ))

        self.container = region

    def getContainer(self, nwbfile):
        self.table = nwbfile.electrodes
        return nwbfile.get_acquisition('test_data').electrodes

    def test_roundtrip(self):
        super(TestElectrodesRegion, self).test_roundtrip()

        for ii, item in enumerate(self.read_container):
            self.assertEqual(self.table[ii+1], item)

    def actOnContainer(self, nwbfile):
        region = nwbfile.create_electrode_table_region(
            region=tuple([1, 2, 3]),
            name='electrodes',
            description='desc'
        )
        nwbfile.add_acquisition(pynwb.ecephys.ElectricalSeries(
            name='test_data2',
            data=np.arange(10),
            timestamps=np.arange(10),
            electrodes=region
        ))
