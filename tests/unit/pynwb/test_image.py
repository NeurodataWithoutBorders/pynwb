import unittest

from pynwb import TimeSeries
from pynwb.image import ImageSeries, IndexSeries, ImageMaskSeries, OpticalSeries, ImageSegmentation, PlaneSegmentation, ROI, ImagingPlane, OpticalChannel

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

        roi1 = ROI('roi1', 'roi description1', pix_mask, pix_mask_weight, img_mask, iSS)
        roi2 = ROI('roi2', 'roi description2', pix_mask, pix_mask_weight, img_mask, iSS)
        roi_list = (roi1, roi2)

        oc = OpticalChannel('description', 'emission_lambda')
        ip = ImagingPlane(oc, 'description', 'device', 'excitation_lambda', 'imaging_rate', 'indicator', 'location', (1, 2, 1, 2, 3), 4.0, 'unit', 'reference_frame')

        ps = PlaneSegmentation('name', 'description', roi_list, ip, iSS)

        iS = ImageSegmentation('test_iS', ps)
        self.assertEqual(iS.source, 'test_iS')
        self.assertEqual(iS.plane_segmentation, ps)

class PlaneSegmentationConstructor(unittest.TestCase):
    def test_init(self):
        w, h = 5, 5;
        img_mask = [[0 for x in range(w)] for y in range(h)] 
        w, h = 5, 2;
        pix_mask = [[0 for x in range(w)] for y in range(h)]
        pix_mask_weight = [0 for x in range(w)]
        iSS = ImageSeries('test_iS', 'a hypothetical source', list(), 'unit', ['external_file'], [1, 2, 3], 'tiff', timestamps=list())

        roi1 = ROI('roi1', 'roi description1', pix_mask, pix_mask_weight, img_mask, iSS)
        roi2 = ROI('roi2', 'roi description2', pix_mask, pix_mask_weight, img_mask, iSS)
        roi_list = (roi1, roi2)

        oc = OpticalChannel('description', 'emission_lambda')
        ip = ImagingPlane(oc, 'description', 'device', 'excitation_lambda', 'imaging_rate', 'indicator', 'location', (1, 2, 1, 2, 3), 4.0, 'unit', 'reference_frame')

        iS = PlaneSegmentation('name', 'description', roi_list, ip, iSS)
        self.assertEqual(iS.name, 'name')
        self.assertEqual(iS.description, 'description')
        self.assertEqual(iS.roi_list, roi_list)
        self.assertEqual(iS.imaging_plane, ip)
        self.assertEqual(iS.reference_images, iSS)

if __name__ == '__main__':
    unittest.main()

