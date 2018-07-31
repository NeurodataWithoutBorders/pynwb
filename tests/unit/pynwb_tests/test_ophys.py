import unittest

from pynwb.ophys import TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence, PlaneSegmentation, \
    ImageSegmentation, OpticalChannel, ImagingPlane, MotionCorrection, CorrectedImageStack
from pynwb.image import ImageSeries
from pynwb.base import TimeSeries

import numpy as np


def CreatePlaneSegmentation():
    w, h = 5, 5
    img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
    pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                [7, 8, 2.0], [9, 10, 2.0]]

    iSS = ImageSeries(name='test_iS', source='a hypothetical source', data=list(), unit='unit',
                      external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())

    oc = OpticalChannel('test_optical_channel', 'test_source', 'description', 500.)
    ip = ImagingPlane('test_imaging_plane', 'test_source', oc, 'description', 'device', 600.,
                      'imaging_rate', 'indicator', 'location', (.1, .2), (0., 0.), 'reference_frame')

    pS = PlaneSegmentation('test source', 'description', ip, 'test_name', iSS)
    pS.add_roi("1234", pix_mask[0:3], img_mask[0])
    pS.add_roi("5678", pix_mask[3:5], img_mask[1])
    return pS


class TwoPhotonSeriesConstructor(unittest.TestCase):
    def test_init(self):
        oc = OpticalChannel('test_name', 'test_source', 'description', 500.)
        self.assertEqual(oc.description, 'description')
        self.assertEqual(oc.emission_lambda, 500.)

        ip = ImagingPlane('test_imaging_plane', 'test source', oc, 'description', 'device', 600.,
                          'imaging_rate', 'indicator', 'location', (.1, .2), (.0, .0), 'reference_frame')
        self.assertEqual(ip.optical_channel[0], oc)
        self.assertEqual(ip.device, 'device')
        self.assertEqual(ip.excitation_lambda, 600.)
        self.assertEqual(ip.imaging_rate, 'imaging_rate')
        self.assertEqual(ip.indicator, 'indicator')
        self.assertEqual(ip.location, 'location')
        self.assertEqual(ip.pixel_origin, (.0, .0))
        self.assertEqual(ip.pixel_deltas, (.1, .2))
        self.assertEqual(ip.reference_frame, 'reference_frame')

        tPS = TwoPhotonSeries('test_tPS', 'a hypothetical source', data=list(), unit='unit', field_of_view=list(),
                              imaging_plane=ip, pmt_gain=1.0, scan_line_rate=2.0, external_file=['external_file'],
                              starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        self.assertEqual(tPS.name, 'test_tPS')
        self.assertEqual(tPS.source, 'a hypothetical source')
        self.assertEqual(tPS.unit, 'unit')
        self.assertEqual(tPS.field_of_view, list())
        self.assertEqual(tPS.imaging_plane, ip)
        self.assertEqual(tPS.pmt_gain, 1.0)
        self.assertEqual(tPS.scan_line_rate, 2.0)
        self.assertEqual(tPS.external_file, ['external_file'])
        self.assertEqual(tPS.starting_frame, [1, 2, 3])
        self.assertEqual(tPS.format, 'tiff')
        self.assertEqual(tPS.dimension, [np.nan])


class MotionCorrectionConstructor(unittest.TestCase):
    def test_init(self):
        mc = MotionCorrection('test_mc', list())
        self.assertEqual(mc.source, 'test_mc')


class CorrectedImageStackConstructor(unittest.TestCase):
    def test_init(self):
        is1 = ImageSeries(name='is1', source='a hypothetical source', data=list(), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        is2 = ImageSeries(name='is2', source='a hypothetical source', data=list(), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        cis = CorrectedImageStack("CorrectedImageStackConstructor", is1, is2, ts)
        self.assertEqual(cis.source, "CorrectedImageStackConstructor")
        self.assertEqual(cis.corrected, is1)
        self.assertEqual(cis.original, is2)
        self.assertEqual(cis.xy_translation, ts)


class RoiResponseSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[1])

        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', rt_region, timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.source, 'a hypothetical source')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.rois, rt_region)


class DfOverFConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[1])

        rrs = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', rt_region, timestamps=list())

        dof = DfOverF('test_dof', rrs)
        self.assertEqual(dof.source, 'test_dof')
        self.assertEqual(dof.roi_response_series['test_ts'], rrs)


class FluorescenceConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[1])

        ts = RoiResponseSeries('test_ts', 'a hypothetical source', list(), 'unit', rt_region, timestamps=list())

        ff = Fluorescence('test_ff', ts)
        self.assertEqual(ff.source, 'test_ff')
        self.assertEqual(ff.roi_response_series['test_ts'], ts)
        self.assertEqual(ff.roi_response_series['test_ts'], ts)


class ImageSegmentationConstructor(unittest.TestCase):

    def test_init(self):
        ps = CreatePlaneSegmentation()

        iS = ImageSegmentation('test_source', ps, name='test_iS')
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'test_source')
        self.assertEqual(iS.plane_segmentations[ps.name], ps)
        self.assertEqual(iS[ps.name], iS.plane_segmentations[ps.name])


class PlaneSegmentationConstructor(unittest.TestCase):
    def test_init(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        iSS = ImageSeries(name='test_iS', source='a hypothetical source', data=list(), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())

        oc = OpticalChannel('test_optical_channel', 'test_source', 'description', 500.)
        ip = ImagingPlane('test_imaging_plane', 'test_source', oc, 'description', 'device', 600.,
                          'imaging_rate', 'indicator', 'location', (.1, .2), (0., 0.), 'reference_frame')

        pS = PlaneSegmentation('test source', 'description', ip, 'test_name', iSS)
        pS.add_roi("1234", pix_mask[0:3], img_mask[0])
        pS.add_roi("5678", pix_mask[3:5], img_mask[1])

        self.assertEqual(pS.description, 'description')
        self.assertEqual(pS.source, 'test source')

        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, iSS)
        self.assertEqual(pS.pixel_masks.data, pix_mask)
        self.assertEqual(pS.image_masks.data, img_mask)


if __name__ == '__main__':
    unittest.main()
