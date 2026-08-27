import warnings
from datetime import datetime

import h5py
import numpy as np
from dateutil.tz import tzutc

from pynwb import NWBFile, NWBHDF5IO
from pynwb.base import Image, ImageReferences, Images
from pynwb.device import Device
from pynwb.image import ImageSeries, IndexSeries, OpticalSeries
from pynwb.testing import AcquisitionH5IOMixin, NWBH5IOMixin, TestCase, remove_test_file


class TestImageSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test ImageSeries to read/write """
        self.dev1 = Device(name='dev1')
        iS = ImageSeries(
            name='test_iS',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            timestamps=[1., 2., 3.],
            device=self.dev1,
        )
        return iS

    def addContainer(self, nwbfile):
        """ Add the test ImageSeries to the given NWBFile """
        nwbfile.add_device(self.dev1)
        super().addContainer(nwbfile)


class TestImageSeriesWithNumSamplesIO(AcquisitionH5IOMixin, TestCase):
    """Roundtrip test for ImageSeries with num_samples (external file + rate timing)."""

    def setUpContainer(self):
        self.dev1 = Device(name='dev1')
        iS = ImageSeries(
            name='test_iS_num_samples',
            unit='Frames',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            rate=30.0,
            num_samples=900,
            device=self.dev1,
        )
        return iS

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.dev1)
        super().addContainer(nwbfile)

    def test_num_samples_written_as_uint32(self):
        """An explicitly set num_samples should be written with the schema dtype (uint32)."""
        read_container = self.roundtripContainer()
        self.assertEqual(read_container.num_samples, 900)
        with h5py.File(self.filename, 'r') as infile:
            dset = infile['acquisition'][self.container.name]['num_samples']
            self.assertEqual(dset.dtype, np.uint32)
            self.assertEqual(dset[()], 900)


class TestImageSeriesDerivedNumSamplesIO(AcquisitionH5IOMixin, TestCase):
    """Roundtrip test for an ImageSeries with internal data and no explicit num_samples."""

    def setUpContainer(self):
        return ImageSeries(
            name='test_iS_derived_num_samples',
            data=np.zeros((10, 5, 5), dtype=np.uint8),
            unit='n.a.',
            rate=1.0,
        )

    def test_derived_num_samples_not_written(self):
        """num_samples derived from len(data) should not be persisted."""
        self.assertIsNone(self.container._num_samples)
        self.assertEqual(self.container.num_samples, 10)  # derived from len(data)

        read_container = self.roundtripContainer()
        with h5py.File(self.filename, 'r') as infile:
            self.assertNotIn('num_samples', infile['acquisition'][self.container.name])

        # the value is still available in memory, derived from the data that was read back
        self.assertIsNone(read_container._num_samples)
        self.assertEqual(read_container.num_samples, 10)


class TestImageSeriesNumSamplesWriteWarnings(TestCase):
    """Writing num_samples should not emit a DtypeConversionWarning. See #2227."""

    def setUp(self):
        self.filename = 'test_image_series_num_samples.nwb'

    def tearDown(self):
        remove_test_file(self.filename)

    def write_and_collect_warnings(self, image_series):
        nwbfile = NWBFile(
            session_description='a file to test writing ImageSeries.num_samples',
            identifier='TEST_num_samples',
            session_start_time=datetime(1971, 1, 1, 12, tzinfo=tzutc()),
        )
        nwbfile.add_acquisition(image_series)
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            with NWBHDF5IO(self.filename, mode='w') as write_io:
                write_io.write(nwbfile)
        return [str(w.message) for w in ws if 'num_samples' in str(w.message)]

    def test_no_warning_for_derived_num_samples(self):
        image_series = ImageSeries(
            name='test_iS',
            data=np.zeros((10, 5, 5), dtype=np.uint8),
            unit='n.a.',
            rate=1.0,
        )
        self.assertEqual(self.write_and_collect_warnings(image_series), [])

    def test_no_warning_for_explicit_num_samples(self):
        image_series = ImageSeries(
            name='test_iS',
            unit='n.a.',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            rate=30.0,
            num_samples=900,
        )
        self.assertEqual(self.write_and_collect_warnings(image_series), [])


class TestIndexSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test IndexSeries to read/write """
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        self.images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        iS = IndexSeries(
            name='test_iS',
            data=np.uint([1, 2, 3]),
            unit='N/A',
            indexed_images=self.images,
            timestamps=[0.1, 0.2, 0.3]
        )
        return iS

    def addContainer(self, nwbfile):
        """ Add the test IndexSeries to the given NWBFile """
        nwbfile.add_stimulus_template(self.images)
        super().addContainer(nwbfile)


class TestOpticalSeriesIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test OpticalSeries to read/write """
        self.dev1 = Device(name='dev1')
        self.optical_series = OpticalSeries(
            name='OpticalSeries',
            distance=8.,
            field_of_view=(4., 5.),
            orientation='upper left',
            data=np.ones((10, 3, 3)),
            unit='m',
            format='raw',
            timestamps=np.arange(10.),
            device=self.dev1,
        )
        return self.optical_series

    def addContainer(self, nwbfile):
        """ Add the test OpticalSeries to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        """ Return the test OpticalSeries from the given NWBFile """
        return nwbfile.stimulus['OpticalSeries']


class TestOpticalSeriesOptionalFieldsIO(NWBH5IOMixin, TestCase):
    """Test reading/writing OpticalSeries with optional fields omitted"""

    def setUpContainer(self):
        """ Return a test OpticalSeries with optional fields set to None """
        self.dev1 = Device(name='dev1')
        self.optical_series = OpticalSeries(
            name='OpticalSeries',
            data=np.ones((10, 3, 3)),
            unit='m',
            format='raw',
            timestamps=np.arange(10.),
            device=self.dev1,
        )
        return self.optical_series

    def addContainer(self, nwbfile):
        """ Add the test OpticalSeries to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        """ Return the test OpticalSeries from the given NWBFile """
        return nwbfile.stimulus['OpticalSeries']

    def test_optional_fields(self):
        """Test that optional fields are None when omitted"""
        self.assertIsNone(self.optical_series.distance)
        self.assertIsNone(self.optical_series.field_of_view)
        self.assertIsNone(self.optical_series.orientation)


class TestOpticalSeriesWithNumSamplesIO(NWBH5IOMixin, TestCase):
    """Roundtrip test for OpticalSeries with num_samples (external file + rate timing)."""

    def setUpContainer(self):
        self.dev1 = Device(name='dev1')
        self.optical_series = OpticalSeries(
            name='OpticalSeries',
            distance=8.,
            field_of_view=(4., 5.),
            orientation='upper left',
            unit='m',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            rate=30.0,
            num_samples=900,
            device=self.dev1,
        )
        return self.optical_series

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.dev1)
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        return nwbfile.stimulus['OpticalSeries']
