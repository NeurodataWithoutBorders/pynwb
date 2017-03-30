import unittest

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, ImageSegmentation, ImagePlane

import numpy as np


class ImageSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.external_file, ['external_file'])
        self.assertEqual(iS.starting_frame, [1, 2, 3])
        self.assertEqual(iS.format, 'tiff')
        #self.assertEqual(iS.bits_per_pixel, np.nan)
        self.assertEqual(iS.dimension, [np.nan])


class IndexSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        iS = IndexSeries('test_iS', 'a hypothetical source', list(), 'unit', ts, 'index_timeseries_path', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.index_timeseries, ts)
        self.assertEqual(iS.index_timeseries_path, 'index_timeseries_path')

class ImageMaskSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        ims = ImageMaskSeries('test_ims', 'a hypothetical source', list(), 'unit', iS, 'masked_imageseries_path', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ims.name, 'test_ims')
        self.assertEqual(ims.source, 'a hypothetical source')
        self.assertEqual(ims.unit, 'unit')
        self.assertEqual(ims.masked_imageseries, iS)
        self.assertEqual(ims.masked_imageseries_path, 'masked_imageseries_path')
        self.assertEqual(ims.external_file, ['external_file'])
        self.assertEqual(ims.starting_frame, [1, 2, 3])
        self.assertEqual(ims.format, 'tiff')

class OpticalSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = OpticalSeries('test_ts', 'a hypothetical source', list(), 'unit', 1.0, list(), 'orientation', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.source, 'a hypothetical source')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.distance, 1.0)
        self.assertEqual(ts.field_of_view, list())
        self.assertEqual(ts.orientation, 'orientation')
        self.assertEqual(ts.external_file, ['external_file'])
        self.assertEqual(ts.starting_frame, [1, 2, 3])
        self.assertEqual(ts.format, 'tiff')

class ImageSegmentationConstructor(unittest.TestCase):

    def test_init(self):
        ip = ImagePlane()
        iS = ImageSegmentation('test_iS', ip)
        self.assertEqual(iS.source, 'test_iS')
        self.assertEqual(iS.image_plane, ip)

class ImagePlaneConstructor(unittest.TestCase):
    def test_init(self):
        pass

class OpticalChannelConstructor(unittest.TestCase):
    def test_init(self):
        pass


if __name__ == '__main__':
    unittest.main()