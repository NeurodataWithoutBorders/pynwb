import unittest

from pynwb import TimeSeries
from pynwb.ophys import TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries

import numpy as np


class TwoPhotonSeriesConstructor(unittest.TestCase):
    def test_init(self):
        tPS = TwoPhotonSeries('test_tPS', 'a hypothetical source', list(), 'unit', list(), 'imaging_plane', 1.0, 2.0, ['external_file'], [1, 2, 3], 'tiff', timestamps=list())
        self.assertEqual(tPS.name, 'test_tPS')
        self.assertEqual(tPS.source, 'a hypothetical source')
        self.assertEqual(tPS.unit, 'unit')
        self.assertEqual(tPS.field_of_view, list())
        self.assertEqual(tPS.imaging_plane, 'imaging_plane')
        self.assertEqual(tPS.pmt_gain, 1.0)
        self.assertEqual(tPS.scan_line_rate, 2.0)
        self.assertEqual(tPS.external_file, ['external_file'])
        self.assertEqual(tPS.starting_frame, [1, 2, 3])
        self.assertEqual(tPS.format, 'tiff')
        self.assertEqual(tPS.dimension, [np.nan])

class RoiResponseSeriesConstructor(unittest.TestCase):
    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], iS, 'segmenttation_interface_path', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.source, 'a hypothetical source')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.roi_names, ['name1'])
        self.assertEqual(ts.segmenttation_interface, iS)
        self.assertEqual(ts.segmenttation_interface_path, 'segmenttation_interface_path')

class DfOverFConstructor(unittest.TestCase):
    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        rrs = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], iS, 'segmenttation_interface_path', timestamps=list())
        dof = DfOverF('test_dof', rrs)
        self.assertEqual(dof.source, 'test_dof')
        self.assertEqual(dof._RoiResponseSeries, rrs)

class FluorescenceConstructor(unittest.TestCase):
    def test_init(self):
        iS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', np.nan, [np.nan], timestamps=list())
        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', ['name1'], iS, 'segmenttation_interface_path', timestamps=list())
        ff = Fluorescence('test_ff', ts)
        self.assertEqual(ff.source, 'test_ff')
        self.assertEqual(ff._RoiResponseSeries, ts)

