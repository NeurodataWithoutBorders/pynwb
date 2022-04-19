import warnings

import numpy as np

from pynwb.base import TimeSeries
from pynwb.image import ImageSeries
from pynwb.ophys import (TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence, PlaneSegmentation,
                         ImageSegmentation, OpticalChannel, ImagingPlane, MotionCorrection, CorrectedImageStack)
from pynwb.testing import TestCase
from pynwb.testing.mock.ophys import mock_ImagingPlane, mock_TwoPhotonSeries, mock_RoiResponseSeries, \
    mock_PlaneSegmentation, mock_OpticalChannel
from pynwb.testing.mock.device import mock_Device


class OpticalChannelConstructor(TestCase):
    def test_init(self):
        oc = OpticalChannel(
            name='test_optical_channel',
            description='description',
            emission_lambda=500.
        )
        self.assertEqual(oc.name, 'test_optical_channel')
        self.assertEqual(oc.description, 'description')
        self.assertEqual(oc.emission_lambda, 500.)


class ImagingPlaneConstructor(TestCase):

    def test_init(self):

        oc, device = mock_OpticalChannel(), mock_Device()

        ip = ImagingPlane(
            name='test_imaging_plane',
            optical_channel=oc,
            description='description',
            device=device,
            excitation_lambda=600.,
            imaging_rate=300.,
            indicator='indicator',
            location='location',
            reference_frame='reference_frame',
            origin_coords=[10, 20],
            origin_coords_unit='oc_unit',
            grid_spacing=[1, 2, 3],
            grid_spacing_unit='gs_unit'
        )
        self.assertEqual(ip.optical_channel[0], oc)
        self.assertEqual(ip.device, device)
        self.assertEqual(ip.excitation_lambda, 600.)
        self.assertEqual(ip.imaging_rate, 300.)
        self.assertEqual(ip.indicator, 'indicator')
        self.assertEqual(ip.location, 'location')
        self.assertEqual(ip.reference_frame, 'reference_frame')
        self.assertEqual(ip.origin_coords, [10, 20])
        self.assertEqual(ip.origin_coords_unit, 'oc_unit')
        self.assertEqual(ip.grid_spacing, [1, 2, 3])
        self.assertEqual(ip.grid_spacing_unit, 'gs_unit')

    def test_manifold_deprecated(self):

        msg = "The 'manifold' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            mock_ImagingPlane(manifold=(1, 1, (2, 2, 2)))

    def test_conversion_deprecated(self):

        msg = "The 'conversion' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            mock_ImagingPlane(conversion=2.0)

    def test_unit_deprecated(self):

        msg = "The 'unit' argument is deprecated in favor of 'origin_coords_unit' and 'grid_spacing_unit'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            mock_ImagingPlane(unit='my_unit')


class TwoPhotonSeriesConstructor(TestCase):

    def test_init(self):
        ip = mock_ImagingPlane()
        tPS = TwoPhotonSeries(
            name='test_tPS',
            unit='unit',
            field_of_view=[2., 3.],
            imaging_plane=ip,
            pmt_gain=1.0,
            scan_line_rate=2.0,
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            rate=50.,
        )
        self.assertEqual(tPS.name, 'test_tPS')
        self.assertEqual(tPS.unit, 'unit')
        self.assertEqual(tPS.field_of_view, [2., 3.])
        self.assertEqual(tPS.pmt_gain, 1.0)
        self.assertEqual(tPS.scan_line_rate, 2.0)
        self.assertEqual(tPS.external_file, ['external_file'])
        self.assertEqual(tPS.starting_frame, [1, 2, 3])
        self.assertEqual(tPS.format, 'tiff')
        self.assertIsNone(tPS.dimension)


class MotionCorrectionConstructor(TestCase):
    def test_init(self):
        corrected = ImageSeries(
            name='corrected',
            data=np.ones((1000, 100, 100)),
            unit='na',
            format='raw',
            starting_time=0.0,
            rate=1.0
        )

        xy_translation = TimeSeries(
            name='xy_translation',
            data=np.ones((1000, 2)),
            unit='pixels',
            starting_time=0.0,
            rate=1.0,
        )

        image_series = mock_TwoPhotonSeries()

        corrected_image_stack = CorrectedImageStack(
            corrected=corrected,
            original=image_series,
            xy_translation=xy_translation,
        )

        motion_correction = MotionCorrection(corrected_image_stacks=[corrected_image_stack])
        self.assertEqual(motion_correction.corrected_image_stacks['CorrectedImageStack'], corrected_image_stack)


class CorrectedImageStackConstructor(TestCase):
    def test_init(self):
        is1 = ImageSeries(
            name='corrected',
            data=np.ones((2, 2, 2)),
            unit='unit',
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=[1., 2.]
        )
        is2 = ImageSeries(
            name='is2',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=[1., 2.]
        )
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float64)
        ts = TimeSeries(
            name='xy_translation',
            data=list(range(len(tstamps))),
            unit='unit',
            timestamps=tstamps
        )
        cis = CorrectedImageStack(
            corrected=is1,
            original=is2,
            xy_translation=ts
        )
        self.assertEqual(cis.corrected, is1)
        self.assertEqual(cis.original, is2)
        self.assertEqual(cis.xy_translation, ts)


class RoiResponseSeriesConstructor(TestCase):
    def test_init(self):
        ps = mock_PlaneSegmentation()
        rt_region = ps.create_roi_table_region(description='the second ROI', region=[0])

        ts = RoiResponseSeries(
            name='test_ts',
            data=[1, 2, 3],
            rois=rt_region,
            unit='unit',
            timestamps=[0.1, 0.2, 0.3]
        )
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.rois, rt_region)

    def test_warnings(self):

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            mock_RoiResponseSeries(
                data=np.ones((6, 3)),
                n_rois=2,
                timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                rate=None,
            )
            self.assertEqual(len(w), 1)
            assert (
                    "The second dimension of data does not match the length of rois. Your data may be transposed."
                ) in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            mock_RoiResponseSeries(
                name="test_ts1",
                data=np.ones((2, 6)),
                n_rois=2,
                rate=30000.,
                unit="n.a.",
            )
            self.assertEqual(len(w), 1)
            assert (
               "The second dimension of data does not match the length of rois, but instead the first does. "
               "Data is oriented incorrectly and should be transposed."
                   ) in str(w[-1].message)


class DfOverFConstructor(TestCase):
    def test_init(self):

        rrs = mock_RoiResponseSeries(name='test_ts')

        dof = DfOverF(rrs)
        self.assertEqual(dof.roi_response_series['test_ts'], rrs)


class FluorescenceConstructor(TestCase):
    def test_init(self):

        ts = mock_RoiResponseSeries(name='test_ts')

        ff = Fluorescence(ts)
        self.assertEqual(ff.roi_response_series['test_ts'], ts)


class ImageSegmentationConstructor(TestCase):

    def test_init(self):
        ps = mock_PlaneSegmentation()

        iS = ImageSegmentation(ps, name='test_iS')
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.plane_segmentations[ps.name], ps)
        self.assertEqual(iS[ps.name], iS.plane_segmentations[ps.name])


class PlaneSegmentationConstructor(TestCase):

    def create_basic_plane_segmentation(self):
        """Creates a basic plane segmentation used for testing"""
        iSS, ip = mock_TwoPhotonSeries(), mock_ImagingPlane()

        pS = PlaneSegmentation(
            description='description',
            imaging_plane=ip,
            name='test_name',
            reference_images=iSS
        )
        return iSS, ip, pS

    def test_init(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        iSS, ip, pS = self.create_basic_plane_segmentation()
        pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])

        self.assertEqual(pS.name, 'test_name')
        self.assertEqual(pS.description, 'description')
        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, (iSS,))

        self.assertEqual(pS['pixel_mask'].target.data, pix_mask)
        self.assertEqual(pS['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(pS['pixel_mask'][1], pix_mask[3:5])
        self.assertEqual(pS['image_mask'].data, img_mask)

    def test_init_pixel_mask(self):
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        iSS, ip, pS = self.create_basic_plane_segmentation()
        pS.add_roi(pixel_mask=pix_mask[0:3])
        pS.add_roi(pixel_mask=pix_mask[3:5])

        self.assertEqual(pS.name, 'test_name')
        self.assertEqual(pS.description, 'description')
        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, (iSS,))

        self.assertEqual(pS['pixel_mask'].target.data, pix_mask)
        self.assertEqual(pS['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(pS['pixel_mask'][1], pix_mask[3:5])

    def test_init_voxel_mask(self):
        vox_mask = [[1, 2, 3, 1.0], [3, 4, 1, 1.0], [5, 6, 3, 1.0],
                    [7, 8, 3, 2.0], [9, 10, 2, 2.0]]

        iSS, ip, pS = self.create_basic_plane_segmentation()
        pS.add_roi(voxel_mask=vox_mask[0:3])
        pS.add_roi(voxel_mask=vox_mask[3:5])

        self.assertEqual(pS.name, 'test_name')
        self.assertEqual(pS.description, 'description')
        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, (iSS,))

        self.assertEqual(pS['voxel_mask'].target.data, vox_mask)
        self.assertEqual(pS['voxel_mask'][0], vox_mask[0:3])
        self.assertEqual(pS['voxel_mask'][1], vox_mask[3:5])

    def test_init_image_mask(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]

        iSS, ip, pS = self.create_basic_plane_segmentation()
        pS.add_roi(image_mask=img_mask[0])
        pS.add_roi(image_mask=img_mask[1])

        self.assertEqual(pS.name, 'test_name')
        self.assertEqual(pS.description, 'description')
        self.assertEqual(pS.imaging_plane, ip)
        self.assertEqual(pS.reference_images, (iSS,))

        self.assertEqual(pS['image_mask'].data, img_mask)

    def test_init_3d_image_mask(self):
        img_masks = np.random.randn(2, 20, 30, 4)

        _, _, pS = self.create_basic_plane_segmentation()
        pS.add_roi(image_mask=img_masks[0])
        pS.add_roi(image_mask=img_masks[1])

        self.assertTrue(np.allclose(pS['image_mask'][0], img_masks[0]))
        self.assertTrue(np.allclose(pS['image_mask'][1], img_masks[1]))

    def test_conversion_of_2d_pixel_mask_to_image_mask(self):
        pixel_mask = [[0, 0, 1.0], [1, 0, 2.0], [2, 0, 2.0]]

        _, _, pS = self.create_basic_plane_segmentation()

        img_mask = pS.pixel_to_image(pixel_mask)
        np.testing.assert_allclose(img_mask, np.asarray([[1, 2, 2.0],
                                                         [0, 0, 0.0],
                                                         [0, 0, 0.0]]))

    def test_conversion_of_2d_image_mask_to_pixel_mask(self):
        image_mask = np.asarray([[1.0, 0.0, 0.0],
                                 [0.0, 1.0, 0.0],
                                 [0.0, 0.0, 1.0]])

        _, _, pS = self.create_basic_plane_segmentation()

        pixel_mask = pS.image_to_pixel(image_mask)
        np.testing.assert_allclose(pixel_mask, np.asarray([[0, 0, 1.0], [1, 1, 1.0], [2, 2, 1.0]]))
