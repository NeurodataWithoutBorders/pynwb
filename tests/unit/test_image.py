import unittest

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, RoiResponseSeries

import numpy as np


class ImageSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        pass

class IndexSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        iS = IndexSeries('test_iS', 'a hypothetical source', list(), 'unit', ts, 'index_timeseries_path', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')

class ImageMaskSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        ims = ImageMaskSeries('test_ims', 'a hypothetical source', list(), 'unit', iS, 'masked_imageseries_path', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ims.name, 'test_ims')

class OpticalSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = OpticalSeries('test_ts', 'a hypothetical source', list(), 'unit', 1.0, list(), 'orientation', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

class RoiResponseSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], iS, 'segmenttation_interface_path', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

