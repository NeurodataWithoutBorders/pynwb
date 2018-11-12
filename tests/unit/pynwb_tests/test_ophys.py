import unittest

from pynwb.ophys import TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence, PlaneSegmentation, \
    ImageSegmentation, OpticalChannel, ImagingPlane, MotionCorrection, CorrectedImageStack
from pynwb.image import ImageSeries
from pynwb.base import TimeSeries
from pynwb.device import Device

import numpy as np


def CreatePlaneSegmentation():
    w, h = 5, 5
    img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
    pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                [7, 8, 2.0], [9, 10, 2.0]]

    iSS = ImageSeries(name='test_iS', data=np.ones((2, 2, 2)), unit='unit',
                      external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=[1., 2.])

    oc = OpticalChannel('test_optical_channel', 'description', 500.)
    device = Device(name='device_name')
    ip = ImagingPlane('test_imaging_plane', oc, 'description', device, 600.,
                      300., 'indicator', 'location', (1, 2, 1, 2, 3), 4.0,
                      'unit', 'reference_frame')

    pS = PlaneSegmentation('description', ip, 'test_name', iSS)
    pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
    pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])
    return pS


class TwoPhotonSeriesConstructor(unittest.TestCase):
    def test_init(self):
        oc = OpticalChannel('test_name', 'description', 500.)
        self.assertEqual(oc.description, 'description')
        self.assertEqual(oc.emission_lambda, 500.)

        device = Device(name='device_name')
        ip = ImagingPlane('test_imaging_plane', oc, 'description', device, 600.,
                          300., 'indicator', 'location', (50, 100, 3), 4.0, 'unit', 'reference_frame')
        self.assertEqual(ip.optical_channel[0], oc)
        self.assertEqual(ip.device, device)
        self.assertEqual(ip.excitation_lambda, 600.)
        self.assertEqual(ip.imaging_rate, 300.)
        self.assertEqual(ip.indicator, 'indicator')
        self.assertEqual(ip.location, 'location')
        self.assertEqual(ip.manifold, (50, 100, 3))
        self.assertEqual(ip.conversion, 4.0)
        self.assertEqual(ip.unit, 'unit')
        self.assertEqual(ip.reference_frame, 'reference_frame')

        tPS = TwoPhotonSeries('test_tPS', unit='unit', field_of_view=[2., 3.],
                              imaging_plane=ip, pmt_gain=1.0, scan_line_rate=2.0, external_file=['external_file'],
                              starting_frame=[1, 2, 3], format='tiff', timestamps=list())
        self.assertEqual(tPS.name, 'test_tPS')
        self.assertEqual(tPS.unit, 'unit')
        self.assertEqual(tPS.field_of_view, [2., 3.])
        self.assertEqual(tPS.imaging_plane, ip)
        self.assertEqual(tPS.pmt_gain, 1.0)
        self.assertEqual(tPS.scan_line_rate, 2.0)
        self.assertEqual(tPS.external_file, ['external_file'])
        self.assertEqual(tPS.starting_frame, [1, 2, 3])
        self.assertEqual(tPS.format, 'tiff')
        self.assertEqual(tPS.dimension, [np.nan])

    def test_args(self):
        oc = OpticalChannel('test_name', 'description', 500.)
        device = Device(name='device_name')
        ip = ImagingPlane('test_imaging_plane', oc, 'description', device, 600.,
                          300., 'indicator', 'location', (50, 100, 3), 4.0, 'unit', 'reference_frame')
        with self.assertRaises(ValueError):  # no data or external file
            TwoPhotonSeries('test_tPS', unit='unit', field_of_view=[2., 3.],
                            imaging_plane=ip, pmt_gain=1.0, scan_line_rate=2.0,
                            starting_frame=[1, 2, 3], format='tiff', timestamps=[1., 2.])


class MotionCorrectionConstructor(unittest.TestCase):
    def test_init(self):
        MotionCorrection(list())


class CorrectedImageStackConstructor(unittest.TestCase):
    def test_init(self):
        is1 = ImageSeries(name='is1', data=np.ones((2, 2, 2)), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=[1., 2.])
        is2 = ImageSeries(name='is2', data=np.ones((2, 2, 2)), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=[1., 2.])
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        cis = CorrectedImageStack(is1, is2, ts)
        self.assertEqual(cis.corrected, is1)
        self.assertEqual(cis.original, is2)
        self.assertEqual(cis.xy_translation, ts)


class RoiResponseSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[0])

        ts = RoiResponseSeries('test_ts', list(), 'unit', rt_region, timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.rois, rt_region)


class DfOverFConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[1])

        rrs = RoiResponseSeries('test_ts', list(), 'unit', rt_region, timestamps=list())

        dof = DfOverF(rrs)
        self.assertEqual(dof.roi_response_series['test_ts'], rrs)


class FluorescenceConstructor(unittest.TestCase):
    def test_init(self):
        ip = CreatePlaneSegmentation()

        rt_region = ip.create_roi_table_region('the second ROI', region=[1])

        ts = RoiResponseSeries('test_ts', list(), 'unit', rt_region, timestamps=list())

        ff = Fluorescence(ts)
        self.assertEqual(ff.roi_response_series['test_ts'], ts)
        self.assertEqual(ff.roi_response_series['test_ts'], ts)


class ImageSegmentationConstructor(unittest.TestCase):

    def test_init(self):
        ps = CreatePlaneSegmentation()

        iS = ImageSegmentation(ps, name='test_iS')
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.plane_segmentations[ps.name], ps)
        self.assertEqual(iS[ps.name], iS.plane_segmentations[ps.name])


class PlaneSegmentationConstructor(unittest.TestCase):

    def getBoilerPlateObjects(self):

        iSS = ImageSeries(name='test_iS', data=np.ones((2, 2, 2)), unit='unit',
                          external_file=['external_file'], starting_frame=[1, 2, 3], format='tiff', timestamps=list())

        device = Device(name='device_name')
        oc = OpticalChannel('test_optical_channel', 'description', 500.)
        ip = ImagingPlane('test_imaging_plane', oc, 'description', device, 600.,
                          300., 'indicator', 'location', (1, 2, 1, 2, 3), 4.0, 'unit', 'reference_frame')
        return iSS, ip

    def test_init(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        iSS, ip = self.getBoilerPlateObjects()

        pS = PlaneSegmentation('description', ip, 'test_name', iSS)
        pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])

        self.assertEqual(pS.description, 'description')

        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, iSS)

        self.assertEqual(pS['pixel_mask'].target.data, pix_mask)
        self.assertEqual(pS['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(pS['pixel_mask'][1], pix_mask[3:5])
        self.assertEqual(pS['image_mask'].data, img_mask)

    def test_init_pixel_mask(self):
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        iSS, ip = self.getBoilerPlateObjects()

        pS = PlaneSegmentation('description', ip, 'test_name', iSS)
        pS.add_roi(pixel_mask=pix_mask[0:3])
        pS.add_roi(pixel_mask=pix_mask[3:5])

        self.assertEqual(pS.description, 'description')

        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, iSS)

        self.assertEqual(pS['pixel_mask'].target.data, pix_mask)
        self.assertEqual(pS['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(pS['pixel_mask'][1], pix_mask[3:5])

    def test_init_voxel_mask(self):
        vox_mask = [[1, 2, 3, 1.0], [3, 4, 1, 1.0], [5, 6, 3, 1.0],
                    [7, 8, 3, 2.0], [9, 10, 2, 2.0]]

        iSS, ip = self.getBoilerPlateObjects()

        pS = PlaneSegmentation('description', ip, 'test_name', iSS)
        pS.add_roi(voxel_mask=vox_mask[0:3])
        pS.add_roi(voxel_mask=vox_mask[3:5])

        self.assertEqual(pS.description, 'description')

        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, iSS)

        self.assertEqual(pS['voxel_mask'].target.data, vox_mask)
        self.assertEqual(pS['voxel_mask'][0], vox_mask[0:3])
        self.assertEqual(pS['voxel_mask'][1], vox_mask[3:5])

    def test_init_3d_image_mask(self):
        img_masks = np.random.randn(2, 20, 30, 4)

        iSS, ip = self.getBoilerPlateObjects()

        pS = PlaneSegmentation('description', ip, 'test_name', iSS)
        pS.add_roi(image_mask=img_masks[0])
        pS.add_roi(image_mask=img_masks[1])

        self.assertTrue(np.allclose(pS['image_mask'][0], img_masks[0]))
        self.assertTrue(np.allclose(pS['image_mask'][1], img_masks[1]))

    def test_init_image_mask(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]

        iSS, ip = self.getBoilerPlateObjects()

        pS = PlaneSegmentation('description', ip, 'test_name', iSS)
        pS.add_roi(image_mask=img_mask[0])
        pS.add_roi(image_mask=img_mask[1])

        self.assertEqual(pS.description, 'description')

        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, iSS)

        self.assertEqual(pS['image_mask'].data, img_mask)


if __name__ == '__main__':
    unittest.main()
