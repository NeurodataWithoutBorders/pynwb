import unittest

from hdmf.common import DynamicTableRegion

from pynwb.ecephys import ElectrodeGroup, ElectricalSeries, FilteredEphys, LFP, Clustering, ClusterWaveforms,\
                          SpikeEventSeries, EventWaveform, EventDetection, FeatureExtraction
from pynwb.device import Device
from pynwb.file import ElectrodeTable as get_electrode_table
from pynwb.testing import TestMapRoundTrip, TestDataInterfaceIO

from abc import ABCMeta


class TestElectrodeGroupIO(TestMapRoundTrip):

    def setUpContainer(self):
        self.dev1 = Device('dev1')
        return ElectrodeGroup('elec1', 'a test ElectrodeGroup',
                                       'a nonexistent place',
                                       self.dev1)

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_electrode_group(self.container.name)


class TestElectricalSeriesIO(TestDataInterfaceIO):

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

    def setUpContainer(self):
        self.make_electrode_table(self)
        region = DynamicTableRegion('electrodes', [0, 2], 'the first and third electrodes', self.table)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        ret = ElectricalSeries('test_eS', data, region, channel_conversion=[4., .4], timestamps=timestamps)
        return ret

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
        self.assertIsInstance(row1.iloc[0]['group'], ElectrodeGroup)
        self.assertIsInstance(row2.iloc[0]['group'], ElectrodeGroup)


class TestMultiElectricalSeries(TestDataInterfaceIO, metaclass=ABCMeta):

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

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)

    def setUpContainer(self):
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')


class TestLFP(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = LFP(es)
        return ret


class TestFilteredEphys(TestMultiElectricalSeries):

    def setUpContainer(self):
        es = self.setUpElectricalSeriesContainers()
        ret = FilteredEphys(es)
        return ret


class TestClusteringIO(TestDataInterfaceIO):

    def setUpContainer(self):
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return Clustering("A fake Clustering interface",
                              [0, 1, 2, 0, 1, 2], [100., 101., 102.], [float(i) for i in range(10, 61, 10)])

    def roundtripContainer(self, cache_spec=False):
        # self.reader.read() will throw DeprecationWarning when reading the Clustering object
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super(TestClusteringIO, self).roundtripContainer(cache_spec)


class EventWaveformConstructor(TestDataInterfaceIO):
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


class ClusterWaveformsConstructor(TestDataInterfaceIO):
    def setUpContainer(self):
        times = [1.3, 2.3]
        num = [3, 4]
        peak_over_rms = [5.3, 6.3]
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            self.clustering = Clustering('description', num, peak_over_rms, times)
        means = [[7.3, 7.3]]
        stdevs = [[8.3, 8.3]]
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            cw = ClusterWaveforms(self.clustering, 'filtering', means, stdevs)
        return cw

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.clustering)
        nwbfile.add_acquisition(self.container)

    def roundtripContainer(self, cache_spec=False):
        # self.reader.read() will throw DeprecationWarning when reading the ClusterWaveformsConstructor object
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super(ClusterWaveformsConstructor, self).roundtripContainer(cache_spec)


class FeatureExtractionConstructor(TestDataInterfaceIO):
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


class EventDetectionConstructor(TestDataInterfaceIO):
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
