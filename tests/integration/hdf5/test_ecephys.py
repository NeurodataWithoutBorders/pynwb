from hdmf.common import DynamicTableRegion
from pynwb import NWBFile

from pynwb.ecephys import (
    ElectrodeGroup,
    ElectricalSeries,
    FilteredEphys,
    LFP,
    Clustering,
    ClusterWaveforms,
    SpikeEventSeries,
    EventWaveform,
    EventDetection,
    FeatureExtraction,
)
from pynwb.device import Device
from pynwb.file import ElectrodeTable as get_electrode_table
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, NWBH5IOFlexMixin, TestCase


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


def setup_electrode_table():
    table = get_electrode_table()
    dev1 = Device(name='dev1')
    group = ElectrodeGroup(
        name='tetrode1',
        description='tetrode description',
        location='tetrode location',
        device=dev1
    )
    for i in range(4):
        table.add_row(location='CA1', group=group, group_name='tetrode1')
    return table, group, dev1


class TestElectricalSeriesIO(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "ElectricalSeries"

    def addContainer(self):
        """ Add the test ElectricalSeries and related objects to the given NWBFile """
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=table)
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10., range(10)))
        channel_conversion = [1., 2., 3., 4.]
        filtering = 'Low-pass filter at 300 Hz'
        es = ElectricalSeries(
            name='test_eS',
            data=data,
            electrodes=region,
            channel_conversion=channel_conversion,
            filtering=filtering,
            timestamps=timestamps
        )

        self.nwbfile.add_acquisition(es)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['test_eS']

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


class TestLFPIO(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "LFP"

    def addContainer(self):
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        region1 = DynamicTableRegion(name='electrodes',
                                     data=[0, 2],
                                     description='the first and third electrodes',
                                     table=table)
        region2 = DynamicTableRegion(name='electrodes',
                                     data=[1, 3],
                                     description='the second and fourth electrodes',
                                     table=table)
        data1 = list(zip(range(10), range(10, 20)))
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        timestamps = list(map(lambda x: x/10., range(10)))
        es1 = ElectricalSeries(name='test_eS1', data=data1, electrodes=region1, timestamps=timestamps)
        es2 = ElectricalSeries(name='test_eS2', data=data2, electrodes=region2, channel_conversion=[4., .4],
                               timestamps=timestamps)
        lfp = LFP()
        self.nwbfile.add_acquisition(lfp)
        lfp.add_electrical_series([es1, es2])

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['LFP']


class TestFilteredEphysIO(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "FilteredEphys"

    def addContainer(self):
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        region1 = DynamicTableRegion(name='electrodes',
                                     data=[0, 2],
                                     description='the first and third electrodes',
                                     table=table)
        region2 = DynamicTableRegion(name='electrodes',
                                     data=[1, 3],
                                     description='the second and fourth electrodes',
                                     table=table)
        data1 = list(zip(range(10), range(10, 20)))
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        timestamps = list(map(lambda x: x/10., range(10)))
        es1 = ElectricalSeries(name='test_eS1', data=data1, electrodes=region1, timestamps=timestamps)
        es2 = ElectricalSeries(name='test_eS2', data=data2, electrodes=region2, channel_conversion=[4., .4],
                               timestamps=timestamps)
        fe = FilteredEphys()
        self.nwbfile.add_acquisition(fe)
        fe.add_electrical_series([es1, es2])

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['FilteredEphys']


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

    def roundtripExportContainer(self, cache_spec=False):
        # catch the DeprecationWarning raised when reading the Clustering object from file
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super().roundtripExportContainer(cache_spec)


class EventWaveformConstructor(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "SpikeEventSeries"

    def addContainer(self):
        """ Add the test SpikeEventSeries and related objects to the given NWBFile """
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=table)
        ses = SpikeEventSeries(
            name='test_sES',
            data=((1, 1), (2, 2), (3, 3)),
            timestamps=[0., 1., 2.],
            electrodes=region
        )

        ew = EventWaveform()
        self.nwbfile.add_acquisition(ew)
        ew.add_spike_event_series(ses)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['EventWaveform']


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

    def roundtripExportContainer(self, cache_spec=False):
        # catch the DeprecationWarning raised when reading the Clustering object from file
        with self.assertWarnsWith(DeprecationWarning, 'use pynwb.misc.Units or NWBFile.units instead'):
            return super().roundtripExportContainer(cache_spec)


class FeatureExtractionConstructor(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "FeatureExtraction"

    def addContainer(self):
        """ Add the test FeatureExtraction and related objects to the given NWBFile """
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        event_times = [1.9, 3.5]
        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=table)
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0., 1., 2.], [3., 4., 5.]], [[6., 7., 8.], [9., 10., 11.]]]
        fe = FeatureExtraction(electrodes=region, description=description, times=event_times, features=features)

        self.nwbfile.add_acquisition(fe)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['FeatureExtraction']


class EventDetectionConstructor(NWBH5IOFlexMixin, TestCase):

    def getContainerType(self):
        return "EventDetection"

    def addContainer(self):
        """ Add the test EventDetection and related objects to the given NWBFile """
        table, group, dev1 = setup_electrode_table()
        self.nwbfile.add_device(dev1)
        self.nwbfile.add_electrode_group(group)
        self.nwbfile.set_electrode_table(table)

        region = DynamicTableRegion(name='electrodes',
                                    data=[0, 2],
                                    description='the first and third electrodes',
                                    table=table)
        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        eS = ElectricalSeries(
            name='test_eS',
            data=data,
            electrodes=region,
            timestamps=ts
        )
        eD = EventDetection(
            detection_method='detection_method',
            source_electricalseries=eS,
            source_idx=(1, 2, 3),
            times=(0.1, 0.2, 0.3)
        )

        self.nwbfile.add_acquisition(eS)
        self.nwbfile.add_acquisition(eD)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition['EventDetection']
