import unittest

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, RoiResponseSeries

import numpy as np


class ImageSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = ImageSeries('test_ts', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

class IndexSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = IndexSeries('test_ts', 'a hypothetical source', list(), 'unit', 'timeseries_link', 'index_timeseries_path', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

class ImageMaskSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = ImageMaskSeries('test_ts', 'a hypothetical source', list(), 'unit', 'masked_imageseries', 'masked_imageseries_path', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

class OpticalSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = OpticalSeries('test_ts', 'a hypothetical source', list(), 'unit', 1.0, list(), 'orientation', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

class RoiResponseSeriesConstructor(unittest.TestCase):

    def test_init(self):
        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], 'segmenttation_interface', 'segmenttation_interface_path', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')

