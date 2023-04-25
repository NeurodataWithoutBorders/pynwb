from pynwb.ecephys import (ElectrodeGroup, ElectricalSeries, FilteredEphys, LFP, Clustering, ClusterWaveforms,
                          SpikeEventSeries, EventWaveform, EventDetection, FeatureExtraction)
from pynwb.device import Device
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase, NWBH5IOFlexMixin


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


class ElectricalSeriesIOMixin(NWBH5IOFlexMixin):
    """
    Mixin class for methods to run a roundtrip test writing an NWB file with multiple ElectricalSeries.

    The abstract method setUpContainer needs to be implemented by classes that include this mixin.
        def setUpContainer(self):
            # return a test Container to read/write
    """

    def addAssociatedContainers(self):
        """Add the associated Device, ElectrodeGroup, and electrodes to the file."""
        device = Device(name="dev1")
        self.nwbfile.add_device(device)

        electrode_group = ElectrodeGroup(
            name='tetrode1',
            description='tetrode description',
            location='tetrode location',
            device=device,
        )
        self.nwbfile.add_electrode_group(electrode_group)

        self.nwbfile.add_electrode(location='CA1', group=electrode_group)
        self.nwbfile.add_electrode(location='CA1', group=electrode_group)
        self.nwbfile.add_electrode(location='CA1', group=electrode_group)
        self.nwbfile.add_electrode(location='CA1', group=electrode_group)

        self.nwbfile.create_processing_module(
            name="ecephys",
            description="processed ecephys data"
        )


class TestElectricalSeriesIO(ElectricalSeriesIOMixin, TestCase):

    def getContainerType(self):
        return "an ElectricalSeries object"

    def addContainer(self):
        """Add the test ElectricalSeries and the associated Device, ElectrodeGroup, and electrodes to the file."""
        self.addAssociatedContainers()
        region = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[0, 2],
            description='the first and third electrodes',
        )
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10., range(10)))
        channel_conversion = [1., 2.]
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

    def getContainer(self, nwbfile):
        return nwbfile.acquisition["test_eS"]

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


class MultiElectricalSeriesIOMixin(ElectricalSeriesIOMixin):

    def setUpTwoElectricalSeries(self):
        """ Return two test ElectricalSeries to read/write """
        region1 = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[0, 2],
            description='the first and third electrodes',
        )
        data1 = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10., range(10)))
        channel_conversion = [1., 2.]
        filtering = 'Low-pass filter at 300 Hz'
        es1 = ElectricalSeries(
            name='test_eS1',
            data=data1,
            electrodes=region1,
            channel_conversion=channel_conversion,
            filtering=filtering,
            timestamps=timestamps
        )

        region2 = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[1, 3],
            description='the second and fourth electrodes',
        )
        data2 = list(zip(reversed(range(10)), reversed(range(10, 20))))
        es2 = ElectricalSeries(
            name='test_eS2',
            data=data2,
            electrodes=region2,
            timestamps=timestamps  # link timestamps
        )
        return es1, es2


class TestLFPIO(MultiElectricalSeriesIOMixin, TestCase):

    def getContainerType(self) -> str:
        return "an LFP object"

    def addContainer(self):
        """ Return a test LFP to read/write """
        self.addAssociatedContainers()
        es1, es2 = self.setUpTwoElectricalSeries()
        lfp = LFP([es1, es2])
        self.nwbfile.processing["ecephys"].add(lfp)

    def getContainer(self, nwbfile):
        return nwbfile.processing["ecephys"]["LFP"]


class TestFilteredEphysIO(MultiElectricalSeriesIOMixin, TestCase):

    def getContainerType(self) -> str:
        return "a FilteredEphys object"

    def addContainer(self):
        """ Return a test LFP to read/write """
        self.addAssociatedContainers()
        es1, es2 = self.setUpTwoElectricalSeries()
        fe = FilteredEphys([es1, es2])
        self.nwbfile.processing["ecephys"].add(fe)

    def getContainer(self, nwbfile):
        return nwbfile.processing["ecephys"]["FilteredEphys"]


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


class TestEventWaveform(ElectricalSeriesIOMixin, TestCase):

    def getContainerType(self) -> str:
        return "an EventWaveform object"

    def addContainer(self):
        """ Return a test EventWaveform to read/write """
        self.addAssociatedContainers()
        region = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[0, 2],
            description='the first and third electrodes',
        )
        ses = SpikeEventSeries(name='test_sES',
                               data=((1, 1), (2, 2), (3, 3)),
                               timestamps=[0., 1., 2.],
                               electrodes=region)
        ew = EventWaveform(ses)
        self.nwbfile.add_acquisition(ew)

    def getContainer(self, nwbfile):
        return nwbfile.acquisition["EventWaveform"]


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


class TestFeatureExtraction(ElectricalSeriesIOMixin, TestCase):

    def getContainerType(self) -> str:
        return "a FeatureExtraction object"

    def addContainer(self):
        """ Return a test FeatureExtraction to read/write """
        self.addAssociatedContainers()
        region = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[0, 2],
            description='the first and third electrodes',
        )
        event_times = [1.9, 3.5]
        description = ['desc1', 'desc2', 'desc3']
        features = [[[0., 1., 2.], [3., 4., 5.]], [[6., 7., 8.], [9., 10., 11.]]]
        fe = FeatureExtraction(electrodes=region, description=description, times=event_times, features=features)
        self.nwbfile.add_acquisition(fe)

    def getContainer(self, nwbfile):
        return nwbfile.acquisition["FeatureExtraction"]


class TestEventDetection(ElectricalSeriesIOMixin, TestCase):

    def getContainerType(self) -> str:
        return "an EventDetection object"

    def addContainer(self):
        """ Return a test EventDetection to read/write """
        self.addAssociatedContainers()
        region = self.nwbfile.create_electrode_table_region(
            name='electrodes',
            region=[0, 2],
            description='the first and third electrodes',
        )

        data = list(range(10))
        ts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        es = ElectricalSeries(name='test_eS', data=data, electrodes=region, timestamps=ts)
        self.nwbfile.add_acquisition(es)

        ed = EventDetection(detection_method='detection_method',
                            source_electricalseries=es,
                            source_idx=(1, 2, 3),
                            times=(0.1, 0.2, 0.3))
        self.nwbfile.add_acquisition(ed)

    def getContainer(self, nwbfile):
        return nwbfile.acquisition["EventDetection"]
