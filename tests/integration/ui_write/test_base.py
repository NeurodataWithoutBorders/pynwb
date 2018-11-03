import pandas as pd
from pynwb import TimeSeries
from pynwb.base import DynamicTable
from pynwb.form.build import GroupBuilder, DatasetBuilder

from . import base


class TestTimeSeriesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        return TimeSeries('test_timeseries', list(range(100, 200, 10)),
                          'SIunit', timestamps=list(range(10)), resolution=0.1)

    def setUpBuilder(self):
        return GroupBuilder('test_timeseries',
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'neurodata_type': 'TimeSeries',
                                        'description': 'no description',
                                        'comments': 'no comments',
                                        'help': 'General time series object'},
                            datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                             attributes={'unit': 'SIunit',
                                                                         'conversion': 1.0,
                                                                         'resolution': 0.1}),
                                      'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                   attributes={'unit': 'Seconds', 'interval': 1})})

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_acquisition(self.container.name)


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


class TestUnitsDf(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('units', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.units = DynamicTable.from_dataframe(pd.DataFrame({
            'a': [1, 2, 3],
            'b': ['4', '5', '6']
        }), 'units')
        # reset the thing
        self.container = nwbfile.units

    def getContainer(self, nwbfile):
        return nwbfile.units


class TestElectrodes(base.TestMapRoundTrip):

    def setUpContainer(self):
        return DynamicTable('electrodes', 'metadata about extracellular electrodes')

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        self.dev1 = nwbfile.create_device('dev1')  # noqa: F405
        self.group = nwbfile.create_electrode_group('tetrode1',  # noqa: F405
                                    'tetrode description', 'tetrode location', self.dev1)

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
