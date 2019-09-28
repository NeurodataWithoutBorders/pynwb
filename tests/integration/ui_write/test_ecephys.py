import unittest2 as unittest

from hdmf.build import GroupBuilder, DatasetBuilder, LinkBuilder, ReferenceBuilder

from pynwb.ecephys import ElectrodeGroup, ElectricalSeries, FilteredEphys, LFP, Clustering, ClusterWaveforms,\
                          SpikeEventSeries, EventWaveform, EventDetection, FeatureExtraction
from pynwb.device import Device
from pynwb.core import DynamicTableRegion
from pynwb.file import ElectrodeTable as get_electrode_table

from . import base

from abc import ABCMeta
from six import with_metaclass


class TestElectrodeGroupIO(base.TestMapRoundTrip):

    def setUpContainer(self):
        self.dev1 = Device('dev1')
        return ElectrodeGroup('elec1', 'a test ElectrodeGroup',
                                       'a nonexistent place',
                                       self.dev1)

    def setUpBuilder(self):
        device_builder = GroupBuilder('dev1',
                                      attributes={'neurodata_type': 'Device',
                                                  'namespace': 'core'})
        return GroupBuilder('elec1',
                            attributes={'neurodata_type': 'ElectrodeGroup',
                                        'namespace': 'core',
                                        'description': 'a test ElectrodeGroup',
                                        'location': 'a nonexistent place'},
                            links={
                                'device': LinkBuilder(device_builder, 'device')
                            })

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_electrode_group(self.container.name)


class TestElectricalSeriesIO(base.TestDataInterfaceIO):

    @staticmethod
    def make_electrode_table(self):
        self.table = get_electrode_table()
        self.dev1 = Device('dev1')
        self.group = ElectrodeGroup('tetrode1',
                                    'tetrode description', 'tetrode location', self.dev1)
        self.table.add_row(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                           group_name='tetrode1')
        self.table.add_row(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=self.group,
                           group_name='tetrode1')
        self.table.add_row(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=self.group,
                           group_name='tetrode1')
        self.table.add_row(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                           group_name='tetrode1')

    @staticmethod
    def get_table_builder(self):
        self.device_builder = GroupBuilder('dev1',
                                           attributes={'neurodata_type': 'Device',
                                                       'namespace': 'core'})
        self.eg_builder = GroupBuilder('tetrode1',
                                       attributes={'neurodata_type': 'ElectrodeGroup',
                                                   'namespace': 'core',
                                                   'description': 'tetrode description',
                                                   'location': 'tetrode location'},
                                       links={
                                           'device': LinkBuilder(self.device_builder, 'device')
                                       })

        datasets = [
            DatasetBuilder('id', data=[1, 2, 3, 4],
                           attributes={'neurodata_type': 'ElementIdentifiers', 'namespace': 'core'}),
            DatasetBuilder('x', data=[1.0, 1.0, 1.0, 1.0],
                           attributes={'description': 'the x coordinate of the channel location',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('y', data=[2.0, 2.0, 2.0, 2.0],
                           attributes={'description': 'the y coordinate of the channel location',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('z', data=[3.0, 3.0, 3.0, 3.0],
                           attributes={'description': 'the z coordinate of the channel location',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('imp', data=[-1.0, -2.0, -3.0, -4.0],
                           attributes={'description': 'the impedance of the channel',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('location', data=['CA1', 'CA1', 'CA1', 'CA1'],
                           attributes={'description': 'the location of channel within the subject e.g. brain region',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('filtering', data=['none', 'none', 'none', 'none'],
                           attributes={'description': 'description of hardware filtering',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('group', data=[ReferenceBuilder(self.eg_builder),
                                          ReferenceBuilder(self.eg_builder),
                                          ReferenceBuilder(self.eg_builder),
                                          ReferenceBuilder(self.eg_builder)],
                           attributes={'description': 'a reference to the ElectrodeGroup this electrode is a part of',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
            DatasetBuilder('group_name', data=['tetrode1', 'tetrode1', 'tetrode1', 'tetrode1'],
                           attributes={'description': 'the name of the ElectrodeGroup this electrode is a part of',
                                       'neurodata_type': 'VectorData', 'namespace': 'core'}),
        ]
        return GroupBuilder('electrodes', datasets={d.name: d for d in datasets},
                            attributes={'colnames': (b'x',
                                                     b'y',
                                                     b'z',
                                                     b'imp',
                                                     b'location',
                                                     b'filtering',
                                                     b'group',
                                                     b'group_name'),
                                        'description': 'metadata about extracellular electrodes',
                                        'neurodata_type': 'DynamicTable',
                                        'namespace': 'core'})

    def setUpContainer(self):
        self.make_electrode_table(self)
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        ret = ElectricalSeries('test_eS', data, region, channel_conversion=[4., .4], timestamps=timestamps)
        return ret

    def setUpBuilder(self):
        table_builder = self.get_table_builder(self)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))

        data_builder = DatasetBuilder('data', data,
                                      attributes={'unit': 'volts',
                                                  'conversion': 1.0,
                                                  'resolution': 0.0})
        timestamps_builder = DatasetBuilder('timestamps', timestamps, attributes={'unit': 'seconds', 'interval': 1})
        elec_builder = DatasetBuilder('electrodes', data=[0, 2],
                                      attributes={'neurodata_type': 'DynamicTableRegion',
                                                  'namespace': 'core',
                                                  'table': ReferenceBuilder(table_builder),
                                                  'description': 'the first and third electrodes'})
        return GroupBuilder('test_eS',
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'comments': 'no comments',
                                        'description': 'no description',
                                        'neurodata_type': 'ElectricalSeries'},
                            datasets={'data': data_builder,
                                      'timestamps': timestamps_builder,
                                      'electrodes': elec_builder})

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def test_eg_ref(self):
        read = self.roundtripContainer()
        row1 = read.electrodes[0]
        row2 = read.electrodes[1]
        self.assertIsInstance(row1[7], ElectrodeGroup)
        self.assertIsInstance(row2[7], ElectrodeGroup)


class TestMultiElectricalSeries(with_metaclass(ABCMeta, base.TestDataInterfaceIO)):

    def setUpElectricalSeriesContainers(self):
        TestElectricalSeriesIO.make_electrode_table(self)
        region1 = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        region2 = DynamicTableRegion('electrodes', [1, 3], 'the second and fourth electrodes', self.table)
        data1 = list(zip(range(10), range(10, 20)))
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        timestamps = list(map(lambda x: x/10, range(10)))
        es1 = ElectricalSeries('test_eS1', data1, region1, timestamps=timestamps)
        es2 = ElectricalSeries('test_eS2', data2, region2, channel_conversion=[4., .4], timestamps=timestamps)
        return es1, es2

    def setUpElectricalSeriesBuilders(self):
        table_builder = TestElectricalSeriesIO.get_table_builder(self)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))

        data_builder = DatasetBuilder('data', data,
                                      attributes={'unit': 'volts',
                                                  'conversion': 1.0,
                                                  'resolution': 0.0})
        timestamps_builder = DatasetBuilder('timestamps', timestamps, attributes={'unit': 'seconds', 'interval': 1})
        elec_builder = DatasetBuilder('electrodes', data=[0, 2],
                                      attributes={'neurodata_type': 'DynamicTableRegion',
                                                  'namespace': 'core',
                                                  'table': ReferenceBuilder(table_builder),
                                                  'description': 'the first and third electrodes'})
        es1 = GroupBuilder('test_eS1',
                           attributes={'namespace': base.CORE_NAMESPACE,
                                       'comments': 'no comments',
                                       'description': 'no description',
                                       'neurodata_type': 'ElectricalSeries'},
                           datasets={'data': data_builder,
                                     'timestamps': timestamps_builder,
                                     'electrodes': elec_builder})
        data = list(zip(reversed(range(10)), reversed(range(10, 20))))

        data_builder = DatasetBuilder('data', data,
                                      attributes={'unit': 'volts',
                                                  'conversion': 1.0,
                                                  'resolution': 0.0})
        timestamps_builder = DatasetBuilder('timestamps', timestamps, attributes={'unit': 'seconds', 'interval': 1})
        elec_builder = DatasetBuilder('electrodes', data=[1, 3],
                                      attributes={'neurodata_type': 'DynamicTableRegion',
                                                  'namespace': 'core',
                                                  'table': ReferenceBuilder(table_builder),
                                                  'description': 'the second and fourth electrodes'})
        es2 = GroupBuilder('test_eS2',
                           attributes={'namespace': base.CORE_NAMESPACE,
                                       'comments': 'no comments',
                                       'description': 'no description',
                                       'neurodata_type': 'ElectricalSeries'},
                           datasets={'data': data_builder,
                                     'timestamps': timestamps_builder,
                                     'electrodes': elec_builder})
        return es1, es2

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def setUpContainer(self):
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')

    def setUpBuilder(self):
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')


class TestLFP(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = LFP(es)
        return ret

    def setUpBuilder(self):
        es = self.setUpElectricalSeriesBuilders()
        ret = GroupBuilder('LFP',
                           attributes={'namespace': base.CORE_NAMESPACE,
                                       'neurodata_type': 'LFP'},
                           groups={'test_es1': es[0], 'test_es2': es[1]})
        return ret


class TestFilteredEphys(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = FilteredEphys(es)
        return ret

    def setUpBuilder(self):
        es = self.setUpElectricalSeriesBuilders()
        ret = GroupBuilder('FilteredEphys',
                           attributes={'namespace': base.CORE_NAMESPACE,
                                       'neurodata_type': 'FilteredEphys'},
                           groups={'test_es1': es[0], 'test_es2': es[1]})
        return ret


class TestClusteringIO(base.TestDataInterfaceIO):

    def setUpBuilder(self):
        return GroupBuilder('Clustering',
                            attributes={
                                'neurodata_type': 'Clustering',
                                'namespace': base.CORE_NAMESPACE},
                            datasets={
                                'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
                                'times': DatasetBuilder('times', list(range(10., 61., 10.))),
                                'peak_over_rms': DatasetBuilder('peak_over_rms', [100., 101., 102.]),
                                'description': DatasetBuilder('description', "A fake Clustering interface")})

    def setUpContainer(self):
        with self.assertWarnsRegex(DeprecationWarning, r'use pynwb\.misc\.Units or NWBFile\.units instead'):
            return Clustering("A fake Clustering interface",
                              [0, 1, 2, 0, 1, 2], [100., 101., 102.], [float(i) for i in range(10, 61, 10)])

    def roundtripContainer(self, cache_spec=False):
        # self.reader.read() will throw DeprecationWarning when reading the Clustering object
        with self.assertWarnsRegex(DeprecationWarning, r'use pynwb\.misc\.Units or NWBFile\.units instead'):
            return super(TestClusteringIO, self).roundtripContainer(cache_spec)


class EventWaveformConstructor(base.TestDataInterfaceIO):
    def setUpContainer(self):
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        sES = SpikeEventSeries(
            'test_sES', ((1, 1, 1), (2, 2, 2)), list(range(2)), region)
        ew = EventWaveform(sES)
        return ew

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)


class ClusterWaveformsConstructor(base.TestDataInterfaceIO):
    def setUpContainer(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]
        with self.assertWarnsRegex(DeprecationWarning, r'use pynwb\.misc\.Units or NWBFile\.units instead'):
            self.clustering = Clustering('description', num, peak_over_rms, times)
        means = [[7.3, 7.3]]
        stdevs = [[8.3, 8.3]]
        with self.assertWarnsRegex(DeprecationWarning, r'use pynwb\.misc\.Units or NWBFile\.units instead'):
            cw = ClusterWaveforms(self.clustering, 'filtering', means, stdevs)
        return cw

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.clustering)
        nwbfile.add_acquisition(self.container)

    def roundtripContainer(self, cache_spec=False):
        # self.reader.read() will throw DeprecationWarning when reading the ClusterWaveformsConstructor object
        with self.assertWarnsRegex(DeprecationWarning, r'use pynwb\.misc\.Units or NWBFile\.units instead'):
            return super(ClusterWaveformsConstructor, self).roundtripContainer(cache_spec)


class FeatureExtractionConstructor(base.TestDataInterfaceIO):
    def setUpContainer(self):
        event_times = [1.9, 3.5]
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0., 1., 2.], [3., 4., 5.]], [[6., 7., 8.], [9., 10., 11.]]]
        fe = FeatureExtraction(region, description, event_times, features)
        return fe

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)


class EventDetectionConstructor(base.TestDataInterfaceIO):
    def setUpContainer(self):
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        self.eS = ElectricalSeries('test_eS', data, region, timestamps=ts)
        eD = EventDetection('detection_method', self.eS, (1, 2, 3), (0.1, 0.2, 0.3))
        return eD

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.eS)
        nwbfile.add_acquisition(self.container)
