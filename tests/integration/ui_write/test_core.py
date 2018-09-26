from pynwb.form.build import GroupBuilder, DatasetBuilder

from pynwb.core import DynamicTable

from . import base


class TestDynamicTableIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        return DynamicTable('trials', 'DynamicTable integration test', 'a test table')

    def setUpBuilder(self):
        id_builder = DatasetBuilder('id', data=[],
                                    attributes={
                                         'help': 'unique identifiers for a list of elements',
                                         'namespace': 'core',
                                         'neurodata_type': 'ElementIdentifiers',
                                    })
        return GroupBuilder('trials',
                            attributes={
                                'help': 'A column-centric table',
                                'description': 'a test table',
                                'namespace': 'core',
                                'neurodata_type': 'DynamicTable',
                                'source': 'DynamicTable integration test',
                                'colnames': tuple(),

                            },
                            datasets={'id': id_builder})

    def addContainer(self, nwbfile):
        nwbfile.trials = self.container

    def getContainer(self, nwbfile):
        return nwbfile.trials


class TestTrials(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('trials', 'DynamicTable integration test', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.add_trial_column('foo', 'an int column')
        nwbfile.add_trial_column('bar', 'a float column')
        nwbfile.add_trial_column('baz', 'a string column')
        nwbfile.add_trial_column('qux', 'a boolean column')
        nwbfile.add_trial({'start': 0., 'end': 1., 'foo': 27, 'bar': 28.0, 'baz': "29", 'qux': True})
        nwbfile.add_trial({'start': 2., 'end': 3., 'foo': 37, 'bar': 38.0, 'baz': "39", 'qux': False})
        # reset the thing
        self.container = nwbfile.trials

    def getContainer(self, nwbfile):
        return nwbfile.trials


class TestUnits(base.TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return DynamicTable('units', 'unit table integration test', 'a placeholder table')

    def addContainer(self, nwbfile):
        nwbfile.add_unit_column('foo', 'an int column')
        nwbfile.add_unit({'foo': 27})
        nwbfile.add_unit({'foo': 37})
        # reset the thing
        self.container = nwbfile.units

    def getContainer(self, nwbfile):
        return nwbfile.units
