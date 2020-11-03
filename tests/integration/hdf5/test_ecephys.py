from hdmf.common import DynamicTableRegion

from pynwb.ecephys import ElectrodeGroup, ElectricalSeries, FilteredEphys, LFP, Clustering, ClusterWaveforms,\
                          SpikeEventSeries, EventWaveform, EventDetection, FeatureExtraction
from pynwb.device import Device
from pynwb.file import ElectrodeTable as get_electrode_table
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase


class TestElectrodeGroupIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test ElectrodeGroup to read/write """
        self.dev1 = Device(name='dev1')
        eg = ElectrodeGroup(name='elec1',
                            description='a test ElectrodeGroup',
                            location='a nonexistent place',
                            device=self.dev1)
        return eg

    def addContainer(self, nwbfile):
        """ Add the test ElectrodeGroup to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.container)

    def getContainer(self, nwbfile):
        """ Return the test ElectrodeGroup from the given NWBFile """
        return nwbfile.get_electrode_group(self.container.name)


class TestElectricalSeriesIO(AcquisitionH5IOMixin, TestCase):

    @staticmethod
    def make_electrode_table(self):
        """ Make an electrode table, electrode group, and device """
        self.table = get_electrode_table()
        self.dev1 = Device(name='dev1')
        self.group = ElectrodeGroup(name='tetrode1',
                                    description='tetrode description',
                                    location='tetrode location',
                                    device=self.dev1)
        for i in range(4):
            self.table.add_row(x=i, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                               group_name='tetrode1')

    def setUpContainer(self):
        """ Return the test ElectricalSeries to read/write """
        self.make_electrode_table(self)
        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=self.table)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10., range(10)))
        es = ElectricalSeries(name='test_eS',
                              data=data,
                              electrodes=region,
                              channel_conversion=[4., .4],
                              timestamps=timestamps)
        return es

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
        row1 = read.electrodes[0]
        row2 = read.electrodes[1]
        self.assertIsInstance(row1.iloc[0]['group'], ElectrodeGroup)
        self.assertIsInstance(row2.iloc[0]['group'], ElectrodeGroup)


class MultiElectricalSeriesIOMixin(AcquisitionH5IOMixin):
    """
    Mixin class for methods to run a roundtrip test writing an NWB file with multiple ElectricalSeries.

    The abstract method setUpContainer needs to be implemented by classes that include this mixin.
        def setUpContainer(self):
            # return a test Container to read/write
    """

    def setUpTwoElectricalSeries(self):
        """ Return two test ElectricalSeries to read/write """
        TestElectricalSeriesIO.make_electrode_table(self)
        region1 = DynamicTableRegion(name='electrodes',
                                     data=[0, 2],
                                     description='the first and third electrodes',
                                     table=self.table)
        region2 = DynamicTableRegion(name='electrodes',
                                     data=[1, 3],
                                     description='the second and fourth electrodes',
                                     table=self.table)
        data1 = list(zip(range(10), range(10, 20)))
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        timestamps = list(map(lambda x: x/10., range(10)))
        es1 = ElectricalSeries(name='test_eS1', data=data1, electrodes=region1, timestamps=timestamps)
        es2 = ElectricalSeries(name='test_eS2', data=data2, electrodes=region2, channel_conversion=[4., .4],
                               timestamps=timestamps)
        return es1, es2

    def addContainer(self, nwbfile):
        """ Add the test ElectricalSeries and related objects to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)


class TestLFPIO(MultiElectricalSeriesIOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test LFP to read/write """
        es = self.setUpTwoElectricalSeries()
        lfp = LFP(es)
        return lfp


class TestFilteredEphysIO(MultiElectricalSeriesIOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test FilteredEphys to read/write """
        es = self.setUpTwoElectricalSeries()
        fe = FilteredEphys(es)
        return fe


class TestClusteringIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test Clustering to read/write """
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return Clustering("A fake Clustering interface",
                              [0, 1, 2, 0, 1, 2], [100., 101., 102.], [float(i) for i in range(10, 61, 10)])

    def roundtripContainer(self, cache_spec=False):
        # catch the DeprecationWarning raised when reading the Clustering object from file
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super().roundtripContainer(cache_spec)


class EventWaveformConstructor(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test EventWaveform to read/write """
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=self.table)
        sES = SpikeEventSeries(name='test_sES',
                               data=((1, 1, 1), (2, 2, 2)),
                               timestamps=[0., 1.],
                               electrodes=region)
        ew = EventWaveform(sES)
        return ew

    def addContainer(self, nwbfile):
        """ Add the test EventWaveform and related objects to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)


class ClusterWaveformsConstructor(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test ClusterWaveforms to read/write """
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
        """ Add the test ClusterWaveforms and related objects to the given NWBFile """
        nwbfile.add_acquisition(self.clustering)
        nwbfile.add_acquisition(self.container)

    def roundtripContainer(self, cache_spec=False):
        # catch the DeprecationWarning raised when reading the Clustering object from file
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super().roundtripContainer(cache_spec)


class FeatureExtractionConstructor(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test FeatureExtraction to read/write """
        event_times = [1.9, 3.5]
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=self.table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0., 1., 2.], [3., 4., 5.]], [[6., 7., 8.], [9., 10., 11.]]]
        fe = FeatureExtraction(electrodes=region, description=description, times=event_times, features=features)
        return fe

    def addContainer(self, nwbfile):
        """ Add the test FeatureExtraction and related objects to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.container)


class EventDetectionConstructor(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test EventDetection to read/write """
        TestElectricalSeriesIO.make_electrode_table(self)
        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=self.table)
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.eS = ElectricalSeries(name='test_eS', data=data, electrodes=region, timestamps=ts)
        eD = EventDetection(detection_method='detection_method',
                            source_electricalseries=self.eS,
                            source_idx=(1, 2, 3),
                            times=(0.1, 0.2, 0.3))
        return eD

    def addContainer(self, nwbfile):
        """ Add the test EventDetection and related objects to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_electrode_group(self.group)
        nwbfile.set_electrode_table(self.table)
        nwbfile.add_acquisition(self.eS)
        nwbfile.add_acquisition(self.container)
