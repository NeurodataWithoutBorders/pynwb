import unittest

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, ImageSegmentation, PlaneSegmentation

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

        iS = IndexSeries('test_iS', 'a hypothetical source', list(), 'unit', ts, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'unit')
        self.assertEqual(iS.index_timeseries, ts)

class ImageMaskSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())

        ims = ImageMaskSeries('test_ims', 'a hypothetical source', list(), 'unit', iS, ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ims.name, 'test_ims')
        self.assertEqual(ims.source, 'a hypothetical source')
        self.assertEqual(ims.unit, 'unit')
        self.assertEqual(ims.masked_imageseries, iS)
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
        w, h = 5, 5;
        img_mask = [[0 for x in range(w)] for y in range(h)] 
        w, h = 5, 2;
        pix_mask = [[0 for x in range(w)] for y in range(h)]
        pix_mask_weight = [0 for x in range(w)]
        iSS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        ip = PlaneSegmentation('name', 'roi_name', img_mask, pix_mask, pix_mask_weight, 'roi_description', 'description', 'imaging_plane_name', iSS)

        iS = ImageSegmentation('test_iS', ip)
        self.assertEqual(iS.source, 'test_iS')
        self.assertEqual(iS.plane_segmentation, ip)

class PlaneSegmentationConstructor(unittest.TestCase):
    def test_init(self):
        w, h = 5, 5;
        img_mask = [[0 for x in range(w)] for y in range(h)] 
        w, h = 5, 2;
        pix_mask = [[0 for x in range(w)] for y in range(h)]
        pix_mask_weight = [0 for x in range(w)]
        iSS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        ip = PlaneSegmentation('name', 'roi_name', img_mask, pix_mask, pix_mask_weight, 'roi_description', 'description', 'imaging_plane_name', iSS)

class OpticalChannelConstructor(unittest.TestCase):
    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()

