import numpy as np

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, \
    GrayscaleImage, RGBImage, RGBAImage
from pynwb.testing import TestCase


class ImageSeriesConstructor(TestCase):

    def test_init(self):
        iS = ImageSeries(name='test_iS', data=np.ones((3, 3, 3)), unit='unit',
                         external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.external_file, ['external_file'])
        self.assertEqual(iS.starting_frame, [1, 2, 3])
        self.assertEqual(iS.format, 'tiff')
        # self.assertEqual(iS.bits_per_pixel, np.nan)


class IndexSeriesConstructor(TestCase):

    def test_init(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())
        iS = IndexSeries('test_iS', list(), ts, unit='unit', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.indexed_timeseries, ts)


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
        self.assertEqual(ims.masked_imageseries, iS)
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
