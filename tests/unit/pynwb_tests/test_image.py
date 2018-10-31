import unittest

import numpy as np

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, \
    GrayscaleImage, RGBImage, RGBAImage


class ImageSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries(name='test_iS', source='a hypothetical source', data=list(), unit='unit',
                         external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.external_file, ['external_file'])
        self.assertEqual(iS.starting_frame, [1, 2, 3])
        self.assertEqual(iS.format, 'tiff')
        # self.assertEqual(iS.bits_per_pixel, np.nan)


class IndexSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())

        iS = IndexSeries('test_iS', 'a hypothetical source', list(), 'unit', ts, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.indexed_timeseries, ts)


class ImageMaskSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries(name='test_iS', source='a hypothetical source', data=list(), unit='unit',
                         external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff',
                         timestamps=list())

        ims = ImageMaskSeries(name='test_ims', source='a hypothetical source', data=list(), unit='unit',
                              masked_imageseries=iS, external_file=['external_file'], starting_frame=[1, 2, 3],
                              format='tiff', timestamps=list())
        self.assertEqual(ims.name, 'test_ims')
        self.assertEqual(ims.source, 'a hypothetical source')
        self.assertEqual(ims.unit, 'unit')
        self.assertEqual(ims.masked_imageseries, iS)
        self.assertEqual(ims.external_file, ['external_file'])
        self.assertEqual(ims.starting_frame, [1, 2, 3])
        self.assertEqual(ims.format, 'tiff')


class OpticalSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = OpticalSeries(name='test_ts', source='a hypothetical source', data=list(), unit='unit', distance=1.0,
                           field_of_view=list(), orientation='orientation', external_file=['external_file'],
                           starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.source, 'a hypothetical source')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.distance, 1.0)
        self.assertEqual(ts.field_of_view, list())
        self.assertEqual(ts.orientation, 'orientation')
        self.assertEqual(ts.external_file, ['external_file'])
        self.assertEqual(ts.starting_frame, [1, 2, 3])
        self.assertEqual(ts.format, 'tiff')


class TestImageSubtypes(unittest.TestCase):

    def test_grayscale_image(self):
        GrayscaleImage(name='test_image', data=np.ones((10, 10)))

    def test_rgb_image(self):
        RGBImage(name='test_image', data=np.ones((10, 10, 3)))

    def test_rgba_image(self):
        RGBAImage(name='test_image', data=np.ones((10, 10, 4)))


if __name__ == '__main__':
    unittest.main()
