import numpy as np

from pynwb.base import Image, ImageReferences, Images
from pynwb.device import Device
from pynwb.image import ImageSeries, IndexSeries, OpticalSeries
from pynwb.testing import AcquisitionH5IOMixin, NWBH5IOMixin, TestCase


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
