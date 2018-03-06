import unittest2 as unittest

import numpy as np

from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, RegionBuilder

from pynwb.ecephys import *  # noqa: F403
from pynwb.misc import UnitTimes

from . import base


class TestUnitTimesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        # self.spike_unit1 = SpikeUnit('unit1', [0, 1, 2], 'spike unit1 description', 'spike units source')
        # self.spike_unit2 = SpikeUnit('unit2', [3, 4, 5], 'spike unit2 description', 'spike units source')
        ut = UnitTimes('UnitTimes integration test', name='UnitTimesTest')
        ut.add_spike_times(0, [0, 1, 2])
        ut.add_spike_times(1, [3, 4, 5])
        return ut

    def setUpBuilder(self):
        ids_builder = DatasetBuilder('unit_ids', [0, 1],
                                     attributes={'neurodata_type': 'ElementIdentifiers',
                                                 'namespace': 'core',
                                                 'help': 'unique identifiers for a list of elements'})
        st_builder = DatasetBuilder('spike_times', [0, 1, 2, 3, 4, 5],
                                    attributes={'neurodata_type': 'VectorData',
                                                'namespace': 'core',
                                                'help': 'Values for a list of elements'})
        sti_builder = DatasetBuilder('spike_times_index',
                                     [RegionBuilder(slice(0, 3), st_builder), RegionBuilder(slice(3, 6), st_builder)],
                                     attributes={'neurodata_type': 'VectorIndex',
                                                 'namespace': 'core',
                                                 'help': 'indexes into a list of values for a list of elements'})
        return GroupBuilder('UnitTimesTest',
                            attributes={'neurodata_type': 'UnitTimes',
                                        'namespace': 'core',
                                        'help': 'Estimated spike times from a single unit',
                                        'source': 'UnitTimes integration test'},
                            datasets={'unit_ids': ids_builder,
                                      'spike_times': st_builder,
                                      'spike_times_index': sti_builder})

    def test_get_spike_times(self):
        ut = self.roundtripContainer()
        received = ut.get_unit_spike_times(0)
        self.assertTrue(np.array_equal(received, [0, 1, 2]))
        received = ut.get_unit_spike_times(1)
        self.assertTrue(np.array_equal(received, [3, 4, 5]))


class TestElectrodeGroupIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        self.dev1 = Device('dev1', 'a test source')  # noqa: F405
        return ElectrodeGroup('elec1', 'a test source',  # noqa: F405
                                        'a test ElectrodeGroup',
                                        'a nonexistent place',
                                        self.dev1)

    def setUpBuilder(self):
        device_builder = GroupBuilder('dev1',
                                      attributes={'neurodata_type': 'Device',
                                                  'namespace': 'core',
                                                  'help': 'A recording device e.g. amplifier',
                                                  'source': 'a test source'})
        return GroupBuilder('elec1',
                            attributes={'neurodata_type': 'ElectrodeGroup',
                                        'namespace': 'core',
                                        'help': 'A physical grouping of channels',
                                        'description': 'a test ElectrodeGroup',
                                        'location': 'a nonexistent place',
                                        'source': 'a test source'},
                            links={
                                'device': LinkBuilder('device', device_builder)
                            })

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_electrode_group(self.container.name)


class TestElectricalSeriesIO(base.TestDataInterfaceIO):

    def make_electrode_table(self):
        self.table = ElectrodeTable('electrodes')  # noqa: F405
        self.dev1 = Device('dev1', 'a test source')  # noqa: F405
        self.group = ElectrodeGroup('tetrode1', 'a test source',  # noqa: F405
                                    'tetrode description', 'tetrode location', self.dev1)
        self.table.add_row(1, 1.0, 2.0, 3.0, -1.0, 'CA1', 'none', 'first channel of tetrode', self.group)
        self.table.add_row(2, 1.0, 2.0, 3.0, -2.0, 'CA1', 'none', 'second channel of tetrode', self.group)
        self.table.add_row(3, 1.0, 2.0, 3.0, -3.0, 'CA1', 'none', 'third channel of tetrode', self.group)
        self.table.add_row(4, 1.0, 2.0, 3.0, -4.0, 'CA1', 'none', 'fourth channel of tetrode', self.group)

    def get_table_builder(self):
        return DatasetBuilder('electrodes', self.table.data,
                              attributes={'neurodata_type': 'ElectrodeTable',
                                          'namespace': 'core',
                                          'help': 'a table for storing data about extracellular electrodes'})

    def setUpContainer(self):
        self.make_electrode_table()
        region = ElectrodeTableRegion(self.table, [0, 2], 'the first and third electrodes')  # noqa: F405
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        ret = ElectricalSeries('test_eS', 'a hypothetical source', data, region, timestamps=timestamps)  # noqa: F405
        return ret

    def setUpBuilder(self):
        table_builder = self.get_table_builder()
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        return GroupBuilder('test_eS',
                            attributes={'source': 'a hypothetical source',
                                        'namespace': base.CORE_NAMESPACE,
                                        'comments': 'no comments',
                                        'description': 'no description',
                                        'neurodata_type': 'ElectricalSeries',
                                        'help': 'Stores acquired voltage data from extracellular recordings'},
                            datasets={'data': DatasetBuilder('data',
                                                             data,
                                                             attributes={'unit': 'volt',
                                                                         'conversion': 1.0,
                                                                         'resolution': 0.0}),
                                      'timestamps': DatasetBuilder('timestamps',
                                                                   timestamps,
                                                                   attributes={'unit': 'Seconds', 'interval': 1}),
                                      'electrodes': DatasetBuilder('electrodes', RegionBuilder([0, 2], table_builder),
                                                                  attributes={
                                                                      'neurodata_type': 'ElectrodeTableRegion',
                                                                      'namespace': 'core',
                                                                      'description': 'the first and third electrodes',
                                                                      'help': 'a subset (i.e. slice or region) of an ElectrodeTable'})})  # noqa: E501

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def test_eg_ref(self):
        read = self.roundtripContainer()
        import pdb
        pdb.set_trace()

class TestMultiElectricalSeries(TestElectricalSeriesIO):

    def setUpElectricalSeriesContainers(self):
        self.make_electrode_table()
        region1 = ElectrodeTableRegion(self.table, [0, 2], 'the first and third electrodes')  # noqa: F405
        region2 = ElectrodeTableRegion(self.table, [1, 3], 'the second and fourth electrodes')  # noqa: F405
        data1 = list(zip(range(10), range(10, 20)))
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        timestamps = list(map(lambda x: x/10, range(10)))
        es1 = ElectricalSeries('test_eS1', 'a hypothetical source', data1, region1, timestamps=timestamps)  # noqa: F405
        es2 = ElectricalSeries('test_eS2', 'a hypothetical source', data2, region2, timestamps=timestamps)  # noqa: F405
        return (es1, es2)

    def setUpElectricalSeriesBuilders(self):
        table_builder = self.get_table_builder()
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        es1 = GroupBuilder('test_eS1',
                            attributes={'source': 'a hypothetical source',
                                        'namespace': base.CORE_NAMESPACE,
                                        'comments': 'no comments',
                                        'description': 'no description',
                                        'neurodata_type': 'ElectricalSeries',
                                        'help': 'Stores acquired voltage data from extracellular recordings'},
                            datasets={'data': DatasetBuilder('data',
                                                             data,
                                                             attributes={'unit': 'volt',
                                                                         'conversion': 1.0,
                                                                         'resolution': 0.0}),
                                      'timestamps': DatasetBuilder('timestamps',
                                                                   timestamps,
                                                                   attributes={'unit': 'Seconds', 'interval': 1}),
                                      'electrodes': DatasetBuilder('electrodes', RegionBuilder([0, 2], table_builder),
                                                                   attributes={
                                                                      'neurodata_type': 'ElectrodeTableRegion',
                                                                      'namespace': 'core',
                                                                      'description': 'the first and third electrodes',
                                                                      'help': 'a subset (i.e. slice or region) of an ElectrodeTable'})})  # noqa: E501
        data = list(zip(reversed(range(10)), reversed(range(10, 20))))
        es2 = GroupBuilder('test_eS2',
                            attributes={'source': 'a hypothetical source',
                                        'namespace': base.CORE_NAMESPACE,
                                        'comments': 'no comments',
                                        'description': 'no description',
                                        'neurodata_type': 'ElectricalSeries',
                                        'help': 'Stores acquired voltage data from extracellular recordings'},
                            datasets={'data': DatasetBuilder('data',
                                                             data,
                                                             attributes={'unit': 'volt',
                                                                         'conversion': 1.0,
                                                                         'resolution': 0.0}),
                                      'timestamps': DatasetBuilder('timestamps',
                                                                   timestamps,
                                                                   attributes={'unit': 'Seconds', 'interval': 1}),
                                      'electrodes': DatasetBuilder('electrodes', RegionBuilder([1, 3], table_builder),
                                                                   attributes={
                                                                      'neurodata_type': 'ElectrodeTableRegion',
                                                                      'namespace': 'core',
                                                                      'description': 'the second and fourth electrodes',
                                                                      'help': 'a subset (i.e. slice or region) of an ElectrodeTable'})})  # noqa: E501
        return (es1, es2)

    def setUpContainer(self):
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')

    def setUpBuilder(self):
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')


class TestLFP(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = LFP('LFP roundtrip test', es)  # noqa: F405
        return ret

    def setUpBuilder(self):
        es = self.setUpElectricalSeriesBuilders()
        ret = GroupBuilder('LFP',
                           attributes={'source': 'LFP roundtrip test',
                                       'namespace': base.CORE_NAMESPACE,
                                       'neurodata_type': 'LFP',
                                       'help': ('LFP data from one or more channels. Filter properties should be '
                                                'noted in the ElectricalSeries')},
                           groups={'test_es1': es[0], 'test_es2': es[1]})
        return ret


class TestFilteredEphys(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = FilteredEphys('FilteredEphys roundtrip test', es)  # noqa: F405
        return ret

    def setUpBuilder(self):
        es = self.setUpElectricalSeriesBuilders()
        ret = GroupBuilder('FilteredEphys',
                           attributes={'source': 'FilteredEphys roundtrip test',
                                       'namespace': base.CORE_NAMESPACE,
                                       'neurodata_type': 'FilteredEphys',
                                       'help': ('Ephys data from one or more channels that is subjected to filtering, '
                                                'such as for gamma or theta oscillations (LFP has its own interface). '
                                                'Filter properties should be noted in the ElectricalSeries')},
                           groups={'test_es1': es[0], 'test_es2': es[1]})
        return ret


class TestClusteringIO(base.TestDataInterfaceIO):

    def setUpBuilder(self):
        return GroupBuilder('Clustering',
                            attributes={
                                'help': 'Clustered spike data, whether from automatic clustering tools (eg, klustakwik) or as a result of manual sorting',  # noqa: E501
                                'source': "an example source for Clustering",
                                'neurodata_type': 'Clustering',
                                'namespace': base.CORE_NAMESPACE},
                            datasets={
                                'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
                                'times': DatasetBuilder('times', list(range(10, 61, 10))),
                                'peak_over_rms': DatasetBuilder('peak_over_rms', [100, 101, 102]),
                                'description': DatasetBuilder('description', "A fake Clustering interface")})

    def setUpContainer(self):
        return Clustering("an example source for Clustering", "A fake Clustering interface",  # noqa: F405
                          [0, 1, 2, 0, 1, 2], [100, 101, 102], list(range(10, 61, 10)))
