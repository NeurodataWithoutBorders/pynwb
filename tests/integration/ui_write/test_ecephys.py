from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, RegionBuilder

from pynwb.ecephys import *  # noqa: F403
from pynwb.misc import UnitTimes, SpikeUnit

from . import base


class TestUnitTimesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        self.spike_unit1 = SpikeUnit('unit1', [0, 1, 2], 'spike unit1 description', 'spike units source')
        self.spike_unit2 = SpikeUnit('unit2', [3, 4, 5], 'spike unit2 description', 'spike units source')
        return UnitTimes('unit times source', [self.spike_unit1, self.spike_unit2], name='UnitTimesTest')

    def setUpBuilder(self):
        su1_builder = GroupBuilder('unit1',
                                   datasets={'times': DatasetBuilder('times', [0, 1, 2])},
                                   attributes={'neurodata_type': 'SpikeUnit',
                                               'namespace': 'core',
                                               'unit_description': 'spike unit1 description',
                                               'help': 'Times for a particular UnitTime object',
                                               'source': 'spike units source'})

        su2_builder = GroupBuilder('unit2',
                                   datasets={'times': DatasetBuilder('times', [3, 4, 5])},
                                   attributes={'neurodata_type': 'SpikeUnit',
                                               'namespace': 'core',
                                               'unit_description': 'spike unit2 description',
                                               'help': 'Times for a particular UnitTime object',
                                               'source': 'spike units source'})

        return GroupBuilder('UnitTimesTest',
                            attributes={'neurodata_type': 'UnitTimes',
                                        'namespace': 'core',
                                        'help': 'Estimated spike times from a single unit',
                                        'source': 'unit times source'},
                            groups={'unit1': su1_builder, 'unit2': su2_builder})


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
                                      'electrodes': RegionBuilder('electrodes', [0, 2],
                                                                  table_builder,
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
