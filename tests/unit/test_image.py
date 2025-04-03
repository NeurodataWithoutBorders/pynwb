import warnings

import numpy as np

from pynwb import TimeSeries
from pynwb.base import Image, Images, ImageReferences
from pynwb.device import Device
from pynwb.image import (
    ImageSeries,
    IndexSeries,
    ImageMaskSeries,
    OpticalSeries,
    GrayscaleImage,
    RGBImage,
    RGBAImage,
)
from pynwb.testing import TestCase


class ImageSeriesConstructor(TestCase):

    def test_init(self):
        dev = Device(name='test_device')
        iS = ImageSeries(
            name='test_iS',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            timestamps=[1., 2., 3.],
            device=dev,
        )
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.external_file, ['external_file'])
        self.assertEqual(iS.starting_frame, [0])
        self.assertEqual(iS.format, 'external')
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
            format="external",
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
            format="external",
            timestamps=list()
        )
        self.assertEqual(iS.unit, ImageSeries.DEFAULT_UNIT)

    def test_dimension_error(self):
        """Test that ImageSeries cannot be created with timestamps and data of different lengths."""
        msg = (
            "ImageSeries 'test_iS': Length of data does not match length of timestamps. Your data may be "
            "transposed. Time should be on the 0th dimension"
        )
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(
                name='test_iS',
                data=np.ones((3, 3, 3)),
                unit='Frames',
                timestamps=[1, 2, 3, 4]
            )

    def test_dimension_warning_external_file_with_timestamps(self):
        """Test that warning is not raised when external file is used with timestamps."""
        obj = ImageSeries.__new__(ImageSeries,
                                  container_source=None,
                                  parent=None,
                                  object_id="test",
                                  in_construct_mode=True)
        with warnings.catch_warnings(record=True) as w:
            obj.__init__(
                name='test_iS',
                external_file=['external_file'],
                format='external',
                unit='Frames',
                starting_frame=[0],
                timestamps=[1, 2, 3, 4]
            )
            self.assertEqual(w, [])
        # Disable construct mode. Since we are not using this object any more
        # this is not strictly necessary but is good style in case we expand
        # the test later on
        obj._in_construct_mode = False

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

    def test_external_file_with_incorrect_starting_frame(self):
        """Test that ValueError is raised when the length of starting_frame
        is not the same as the length of external_file."""
        for starting_frame in [None, [0], [1, 2, 3]]:
            with self.subTest():
                msg = (
                    "ImageSeries 'test_iS': The number of frame indices in "
                    "'starting_frame' should have the same length as 'external_file'."
                )
                with self.assertRaisesWith(ValueError, msg):
                    ImageSeries(
                        name="test_iS",
                        external_file=["external_file", "external_file2"],
                        format="external",
                        unit="n.a.",
                        starting_frame=starting_frame,
                        rate=0.2,
                    )

    def test_external_file_with_incorrect_starting_frame_construct_mode(self):
        """Test that warning is raised when the length of starting_frame
        is not the same as the length of external_file in case that the
        ImageSeries in construct mode (i.e., during read)."""
        for starting_frame in [None, [0], [1, 2, 3]]:
            with self.subTest():
                msg = (
                    "ImageSeries 'test_iS': The number of frame indices in "
                    "'starting_frame' should have the same length as 'external_file'."
                )
                # Create the image series in construct mode, modeling the behavior
                # of the ObjectMapper on read while avoiding having to create, write,
                # and read and entire NWB file
                obj = ImageSeries.__new__(ImageSeries,
                                          container_source=None,
                                          parent=None,
                                          object_id="test",
                                          in_construct_mode=True)
                with self.assertWarnsWith(warn_type=UserWarning, exc_msg=msg):
                    obj.__init__(
                        name="test_iS",
                        external_file=["external_file", "external_file2"],
                        format="external",
                        unit="n.a.",
                        starting_frame=starting_frame,
                        rate=0.2,
                    )
            # Disable construct mode. Since we are not using this object any more
            # this is not strictly necessary but is good style in case we expand
            # the test later on
            obj._in_construct_mode = False

    def test_external_file_with_correct_starting_frame(self):
        """Test that ValueError is not raised when the length of starting_frame
        is the same as the length of external_file."""
        with warnings.catch_warnings(record=True) as w:
            ImageSeries(
                name="test_iS",
                external_file=["external_file", "external_file2", "external_file3"],
                format="external",
                unit="n.a.",
                starting_frame=[0, 15, 30],
                rate=0.2,
            )
            self.assertEqual(w, [])

    def test_external_file_with_default_starting_frame(self):
        """Test that starting_frame is set to [0] if not provided, when external_file is has length 1."""
        iS = ImageSeries(
                name="test_iS",
                external_file=["external_file"],
                format="external",
                unit="n.a.",
                starting_frame=None,
                rate=0.2,
        )
        self.assertEqual(iS.starting_frame, [0])

    def test_external_file_with_incorrect_format(self):
        """Test that ValueError is raised when external_file is provided but
        the format is not 'external'."""
        msg = (
            "ImageSeries 'test_iS': Format must be 'external' when external_file is specified."
        )
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(
                name="test_iS",
                external_file=["external_file"],
                format="raw",
                unit="n.a.",
                starting_frame=[0],
                rate=0.2,
            )

    def test_external_file_with_incorrect_format_construct_mode(self):
        """Test that UserWarning is raised when external_file is provided but
        the format is not 'external' while being in construct mode (i.e,. on data read)."""
        obj = ImageSeries.__new__(ImageSeries,
                                  container_source=None,
                                  parent=None,
                                  object_id="test",
                                  in_construct_mode=True)
        msg = (
            "ImageSeries 'test_iS': Format must be 'external' when external_file is specified."
        )
        with self.assertWarnsWith(warn_type=UserWarning, exc_msg=msg):
            obj.__init__(
                name="test_iS",
                external_file=["external_file"],
                format="raw",
                unit="n.a.",
                starting_frame=[0],
                rate=0.2,
            )

    def test_external_file_default_format(self):
        """Test that format is set to 'external' if not provided, when external_file is provided."""

        kwargs = dict(name="test_iS",
                external_file=["external_file", "external_file2"],
                unit="n.a.",
                starting_frame=[0, 10],
                rate=0.2,)
        
        iS = ImageSeries(**kwargs)
        self.assertEqual(iS.format, "external")

    def test_external_file_with_correct_format(self):
        """Test that warning is not raised when external_file is provided and format
        is external."""
        with warnings.catch_warnings(record=True) as w:
            ImageSeries(
                name="test_iS",
                external_file=["external_file"],
                format="external",
                unit="n.a.",
                starting_frame=[0],
                rate=0.2,
            )
            self.assertEqual(w, [])

    def test_external_file_with_data(self):
        """Test that ValueError is raised when external_file is provided and
        data is not None."""
        msg = (
            "ImageSeries 'test_iS': Either external_file or data must be specified (not None), but not both."
        )
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(
                name="test_iS",
                external_file=["external_file"],
                data=np.ones((3, 3, 3)),
                format="external",
                unit="n.a.",
                starting_frame=[0],
                rate=0.2,
            )

    def test_external_file_with_data_construct_mode(self):
        """Test that UserWarning is raised when external_file is provided and
        data is not None while being in construct mode (i.e,. on read)."""
        obj = ImageSeries.__new__(ImageSeries,
                                  container_source=None,
                                  parent=None,
                                  object_id="test",
                                  in_construct_mode=True)
        msg = (
            "ImageSeries 'test_iS': Either external_file or data must be specified (not None), but not both."
        )
        with self.assertWarnsWith(warn_type=UserWarning, exc_msg=msg):
            obj.__init__(
                name="test_iS",
                external_file=["external_file"],
                data=np.ones((3, 3, 3)),
                format="external",
                unit="n.a.",
                starting_frame=[0],
                rate=0.2,
            )


    def test_bits_per_pixel_deprecation(self):
        """Test that bits_per_pixel can be set and that a deprecated warning is raised."""
        msg = "bits_per_pixel is deprecated"
        kwargs = dict(name='test_iS',
                unit='unit',
                external_file=['external_file'],
                starting_frame=[0],
                format='external',
                timestamps=[1., 2., 3.],
                bits_per_pixel=8)
        with self.assertRaisesWith(ValueError, msg):
            ImageSeries(**kwargs)

        # create object in construct mode, modeling the behavior of the ObjectMapper on read
        # no warning or error should be raised
        iS = ImageSeries.__new__(ImageSeries, in_construct_mode=True)
        iS.__init__(**kwargs)


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
        msg = ("The 'unit' field of IndexSeries is fixed to the value 'N/A'.")
        kwargs = dict(name='test_iS',
                data=[1, 2, 3],
                unit='na',
                indexed_timeseries=ts,
                timestamps=[0.1, 0.2, 0.3])

        # create object with deprecated argument
        with self.assertRaisesWith(ValueError, msg):
            IndexSeries(**kwargs)

        # create object in construct mode, modeling the behavior of the ObjectMapper on read
        # no warning or error should be raised
        iS = IndexSeries.__new__(IndexSeries, in_construct_mode=True)
        iS.__init__(**kwargs)

        self.assertEqual(iS.unit, 'N/A')

    def test_init_indexed_ts(self):
        ts = TimeSeries(
            name='test_ts',
            data=[1, 2, 3],
            unit='unit',
            timestamps=[0.1, 0.2, 0.3]
        )
        msg = ("The indexed_timeseries field of IndexSeries is deprecated. "
               "Use the indexed_images field instead.")
        kwargs = dict(name='test_iS',
                data=[1, 2, 3],
                unit='N/A',
                indexed_timeseries=ts,
                timestamps=[0.1, 0.2, 0.3])
        
        # create object with deprecated argument
        with self.assertRaisesWith(ValueError, msg):
            IndexSeries(**kwargs)

        # create object in construct mode, modeling the behavior of the ObjectMapper on read
        # no warning or error should be raised
        iS = IndexSeries.__new__(IndexSeries, in_construct_mode=True)
        iS.__init__(**kwargs)

        self.assertIs(iS.indexed_timeseries, ts)

    def test_init_no_indexed_ts_or_timeseries(self):
        """Test that an error is raised when neither indexed_timeseries nor indexed_images is provided"""
        msg = ("Either indexed_timeseries or indexed_images "
               "must be provided when creating an IndexSeries.")
        with self.assertRaisesWith(ValueError, msg):
            IndexSeries(name='test_iS', 
                        data=[1, 2, 3], 
                        unit='N/A', 
                        timestamps=[0.1, 0.2, 0.3])

    def test_init_conversion_warning(self):
        """Test that a warning is raised when conversion is provided"""
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        with self.assertWarnsWith(UserWarning, "The conversion attribute is not used by IndexSeries."):
            IndexSeries(
                name='test_iS',
                data=[1, 2, 3],
                unit='N/A',
                indexed_images=images,
                timestamps=[0.1, 0.2, 0.3],
                conversion=5.0
            )

    def test_init_resolution_warning(self):
        """Test that a warning is raised when resolution is provided"""
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        with self.assertWarnsWith(UserWarning, "The resolution attribute is not used by IndexSeries."):
            IndexSeries(
                name='test_iS',
                data=[1, 2, 3],
                unit='N/A',
                indexed_images=images,
                timestamps=[0.1, 0.2, 0.3],
                resolution=1.0
            )

    def test_init_offset_warning(self):
        """Test that a warning is raised when offset is provided"""
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        with self.assertWarnsWith(UserWarning, "The offset attribute is not used by IndexSeries."):
            IndexSeries(
                name='test_iS',
                data=[1, 2, 3],
                unit='N/A',
                indexed_images=images,
                timestamps=[0.1, 0.2, 0.3],
                offset=1.0
            )



class ImageMaskSeriesConstructor(TestCase):

    def test_init(self):
        iS = ImageSeries(name='test_iS', unit='unit',
                         external_file=['external_file'], starting_frame=[0], format='external',
                         timestamps=[1., .2])

        with self.assertRaises(ValueError):
            ImageMaskSeries(name='test_ims', unit='unit',
                              masked_imageseries=iS, external_file=['external_file'], starting_frame=[0],
                              format='external', timestamps=[1., 2.])

class OpticalSeriesConstructor(TestCase):

    def test_init(self):
        ts = OpticalSeries(name='test_ts', unit='unit', distance=1.0,
                           field_of_view=[4, 5], orientation='orientation', external_file=['external_file'],
                           starting_frame=[0], format='external', timestamps=[1., 2.])
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.distance, 1.0)
        self.assertEqual(ts.field_of_view, [4, 5])
        self.assertEqual(ts.orientation, 'orientation')
        self.assertEqual(ts.external_file, ['external_file'])
        self.assertEqual(ts.starting_frame, [0])
        self.assertEqual(ts.format, 'external')


    def test_init_all_optional_fields_none(self):
        """Test that OpticalSeries can be created with all optional fields set to None."""
        ts = OpticalSeries(
            name="test_ts",
            unit="unit",
            external_file=["external_file"],
            starting_frame=[0],
            format="external",
            timestamps=[1.0, 2.0],
        )
        self.assertIsNone(ts.distance)
        self.assertIsNone(ts.field_of_view)
        self.assertIsNone(ts.orientation)

class TestImageSubtypes(TestCase):

    def test_grayscale_image(self):
        GrayscaleImage(name='test_grayscale_image', data=np.ones((2, 2)))

    def test_rgb_image(self):
        RGBImage(name='test_rgb_image', data=np.ones((2, 2, 3)))

    def test_rgba_image(self):
        RGBAImage(name='test_rgba_image', data=np.ones((2, 2, 4)))
