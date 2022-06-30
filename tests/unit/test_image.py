import warnings

import numpy as np

from pynwb import TimeSeries
from pynwb.base import Image, Images, ImageReferences
from pynwb.device import Device
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, GrayscaleImage, RGBImage, RGBAImage
from pynwb.testing import TestCase


class ImageSeriesConstructor(TestCase):

    def test_init(self):
        dev = Device('test_device')
        iS = ImageSeries(
            name='test_iS',
            data=np.ones((3, 3, 3)),
            unit='unit',
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=[1., 2., 3.],
            device=dev,
        )
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.external_file, ['external_file'])
        self.assertEqual(iS.starting_frame, [1, 2, 3])
        self.assertEqual(iS.format, 'tiff')
        self.assertIs(iS.device, dev)
        # self.assertEqual(iS.bits_per_pixel, np.nan)

    def test_no_data_no_file(self):
        msg = "Must supply either external_file or data to ImageSeries 'test_iS'."
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(
                name='test_iS',
                unit='unit',
                rate=2.,
            )

    def test_external_file_no_frame(self):
        iS = ImageSeries(
            name='test_iS',
            unit='unit',
            external_file=['external_file'],
            timestamps=[1., 2., 3.]
        )
        self.assertListEqual(iS.starting_frame, [0])

    def test_data_no_frame(self):
        iS = ImageSeries(
            name='test_iS',
            unit='unit',
            data=np.ones((3, 3, 3)),
            timestamps=[1., 2., 3.]
        )
        self.assertIsNone(iS.starting_frame)

    def test_data_no_unit(self):
        msg = "Must supply 'unit' argument when supplying 'data' to ImageSeries 'test_iS'."
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(
                name='test_iS',
                data=np.ones((3, 3, 3)),
                timestamps=list()
            )

    def test_external_file_no_unit(self):
        iS = ImageSeries(
            name='test_iS',
            external_file=['external_file'],
            timestamps=list()
        )
        self.assertEqual(iS.unit, ImageSeries.DEFAULT_UNIT)

    def test_dimension_warning(self):
        """Test that a warning is raised when the dimensions of the data are not the
        same as the dimensions of the timestamps."""
        msg = (
            "ImageSeries 'test_iS': Length of data does not match length of timestamps. Your data may be "
            "transposed. Time should be on the 0th dimension"
        )
        with self.assertWarnsWith(UserWarning, msg):
            ImageSeries(
                name='test_iS',
                data=np.ones((3, 3, 3)),
                unit='Frames',
                starting_frame=[0],
                timestamps=[1, 2, 3, 4]
            )

    def test_dimension_warning_external_file_with_timestamps(self):
        """Test that a warning is not raised when external file is used with timestamps."""
        with warnings.catch_warnings(record=True) as w:
            ImageSeries(
                name='test_iS',
                external_file=['external_file'],
                format='external',
                unit='Frames',
                starting_frame=[0],
                timestamps=[1, 2, 3, 4]
            )
            self.assertEqual(w, [])

    def test_dimension_warning_external_file_with_rate(self):
        """Test that a warning is not raised when external file is used with rate."""
        with warnings.catch_warnings(record=True) as w:
            ImageSeries(
                name='test_iS',
                external_file=['external_file'],
                format='external',
                unit='Frames',
                starting_frame=[0],
                rate=0.2,
            )
            self.assertEqual(w, [])


class IndexSeriesConstructor(TestCase):

    def test_init(self):
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        iS = IndexSeries(
            name='test_iS',
            data=[1, 2, 3],
            unit='N/A',
            indexed_images=images,
            timestamps=[0.1, 0.2, 0.3]
        )
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'N/A')
        self.assertIs(iS.indexed_images, images)

    def test_init_bad_unit(self):
        ts = TimeSeries(
            name='test_ts',
            data=[1, 2, 3],
            unit='unit',
            timestamps=[0.1, 0.2, 0.3]
        )
        msg = ("The 'unit' field of IndexSeries is fixed to the value 'N/A' starting in NWB 2.5. Passing "
               "a different value for 'unit' will raise an error in PyNWB 3.0.")
        with self.assertWarnsWith(PendingDeprecationWarning, msg):
            iS = IndexSeries(
                name='test_iS',
                data=[1, 2, 3],
                unit='na',
                indexed_timeseries=ts,
                timestamps=[0.1, 0.2, 0.3]
            )
        self.assertEqual(iS.unit, 'N/A')

    def test_init_indexed_ts(self):
        ts = TimeSeries(
            name='test_ts',
            data=[1, 2, 3],
            unit='unit',
            timestamps=[0.1, 0.2, 0.3]
        )
        msg = ("The indexed_timeseries field of IndexSeries is discouraged and will be deprecated in "
               "a future version of NWB. Use the indexed_images field instead.")
        with self.assertWarnsWith(PendingDeprecationWarning, msg):
            iS = IndexSeries(
                name='test_iS',
                data=[1, 2, 3],
                unit='N/A',
                indexed_timeseries=ts,
                timestamps=[0.1, 0.2, 0.3]
            )
        self.assertIs(iS.indexed_timeseries, ts)


class ImageMaskSeriesConstructor(TestCase):

    def test_init(self):
        iS = ImageSeries(name='test_iS', data=np.ones((2, 2, 2)), unit='unit',
                         external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff',
                         timestamps=[1., .2])

        ims = ImageMaskSeries(name='test_ims', data=np.ones((2, 2, 2)), unit='unit',
                              masked_imageseries=iS, external_file=['external_file'], starting_frame=[1, 2, 3],
                              format='tiff', timestamps=[1., 2.])
        self.assertEqual(ims.name, 'test_ims')
        self.assertEqual(ims.unit, 'unit')
        self.assertIs(ims.masked_imageseries, iS)
        self.assertEqual(ims.external_file, ['external_file'])
        self.assertEqual(ims.starting_frame, [1, 2, 3])
        self.assertEqual(ims.format, 'tiff')


class OpticalSeriesConstructor(TestCase):

    def test_init(self):
        ts = OpticalSeries(name='test_ts', data=np.ones((2, 2, 2)), unit='unit', distance=1.0,
                           field_of_view=[4, 5], orientation='orientation', external_file=['external_file'],
                           starting_frame=[1, 2, 3], format='tiff', timestamps=[1., 2.])
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.distance, 1.0)
        self.assertEqual(ts.field_of_view, [4, 5])
        self.assertEqual(ts.orientation, 'orientation')
        self.assertEqual(ts.external_file, ['external_file'])
        self.assertEqual(ts.starting_frame, [1, 2, 3])
        self.assertEqual(ts.format, 'tiff')


class TestImageSubtypes(TestCase):

    def test_grayscale_image(self):
        GrayscaleImage(name='test_grayscale_image', data=np.ones((2, 2)))

    def test_rgb_image(self):
        RGBImage(name='test_rgb_image', data=np.ones((2, 2, 3)))

    def test_rgba_image(self):
        RGBAImage('test_rgba_image', np.ones((2, 2, 4)))
