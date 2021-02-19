import numpy as np
import pytest

from pynwb.base import TimeSeries
from pynwb.image import ImageSeries
from pynwb.ophys import (TwoPhotonSeries, RoiResponseSeries, DfOverF, Fluorescence, PlaneSegmentation,
                         ImageSegmentation, OpticalChannel, ImagingPlane, MotionCorrection, CorrectedImageStack)
from pynwb.testing import TestCase
from pynwb.testing.fixtures.ophys import optical_channel, imaging_plane, plane_segmentation
from pynwb.testing.fixtures.device import device


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


@pytest.mark.usefixtures("optical_channel", "device_fixture")
class ImagingPlaneConstructor(TestCase):

    def test_init(self, optical_channel, device_fixture):

        ip = ImagingPlane(
            name='test_imaging_plane',
            optical_channel=optical_channel,
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
        self.assertEqual(ip.optical_channel[0], optical_channel)
        self.assertEqual(ip.device, device_fixture)
        self.assertEqual(ip.excitation_lambda, 600.)
        self.assertEqual(ip.imaging_rate, 300.)
        self.assertEqual(ip.indicator, 'indicator')
        self.assertEqual(ip.location, 'location')
        self.assertEqual(ip.reference_frame, 'reference_frame')
        self.assertEqual(ip.origin_coords, [10, 20])
        self.assertEqual(ip.origin_coords_unit, 'oc_unit')
        self.assertEqual(ip.grid_spacing, [1, 2, 3])
        self.assertEqual(ip.grid_spacing_unit, 'gs_unit')

    def test_manifold_deprecated(self, optical_channel):

        msg = "The 'manifold' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            ImagingPlane(
                name='test_imaging_plane',
                optical_channel=optical_channel,
                description='description',
                device=device,
                excitation_lambda=600.,
                imaging_rate=300.,
                indicator='indicator',
                location='location',
                manifold=(1, 1, (2, 2, 2))
            )

    def test_conversion_deprecated(self, optical_channel):

        msg = "The 'conversion' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            ImagingPlane(
                name='test_imaging_plane',
                optical_channel=optical_channel,
                description='description',
                device=device,
                excitation_lambda=600.,
                imaging_rate=300.,
                indicator='indicator',
                location='location',
                conversion=2.0
            )

    def test_unit_deprecated(self):

        msg = "The 'unit' argument is deprecated in favor of 'origin_coords_unit' and 'grid_spacing_unit'."
        with self.assertWarnsWith(DeprecationWarning, msg):
            ImagingPlane(
                name='test_imaging_plane',
                optical_channel=optical_channel,
                description='description',
                device=device,
                excitation_lambda=600.,
                imaging_rate=300.,
                indicator='indicator',
                location='location',
                reference_frame='reference_frame',
                unit='my_unit'
            )


@pytest.mark.usefixtures("imaging_plane")
class TwoPhotonSeriesConstructor(TestCase):

    def test_init(self, imaging_plane):
        tPS = TwoPhotonSeries(
            name='test_tPS',
            unit='unit',
            field_of_view=[2., 3.],
            imaging_plane=imaging_plane,
            pmt_gain=1.0,
            scan_line_rate=2.0,
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=list()
        )
        self.assertEqual(tPS.name, 'test_tPS')
        self.assertEqual(tPS.unit, 'unit')
        self.assertEqual(tPS.field_of_view, [2., 3.])
        self.assertEqual(tPS.imaging_plane, imaging_plane)
        self.assertEqual(tPS.pmt_gain, 1.0)
        self.assertEqual(tPS.scan_line_rate, 2.0)
        self.assertEqual(tPS.external_file, ['external_file'])
        self.assertEqual(tPS.starting_frame, [1, 2, 3])
        self.assertEqual(tPS.format, 'tiff')
        self.assertIsNone(tPS.dimension)


class MotionCorrectionConstructor(TestCase):
    def test_init(self):
        MotionCorrection(list())


class CorrectedImageStackConstructor(TestCase):
    def test_init(self):
        is1 = ImageSeries(
            name='is1',
            data=np.ones((2, 2, 2)),
            unit='unit',
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=[1., 2.]
        )
        is2 = ImageSeries(
            name='is2',
            data=np.ones((2, 2, 2)),
            unit='unit',
            external_file=['external_file'],
            starting_frame=[1, 2, 3],
            format='tiff',
            timestamps=[1., 2.]
        )
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries(
            name="test_ts",
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
    def test_init(self, plane_segmentation):
        rt_region = plane_segmentation.create_roi_table_region(description='the second ROI', region=[0])

        ts = RoiResponseSeries(
            name='test_ts',
            data=list(),
            rois=rt_region,
            unit='unit',
            timestamps=list()
        )
        self.assertEqual(ts.name, 'test_ts')
        self.assertEqual(ts.unit, 'unit')
        self.assertEqual(ts.rois, rt_region)


class DfOverFConstructor(TestCase):
    def test_init(self):
        rt_region = plane_segmentation.create_roi_table_region(description='the second ROI', region=[1])

        rrs = RoiResponseSeries(
            name='test_ts',
            data=list(),
            rois=rt_region,
            unit='unit',
            timestamps=list()
        )

        dof = DfOverF(rrs)
        self.assertEqual(dof.roi_response_series['test_ts'], rrs)


class FluorescenceConstructor(TestCase):
    def test_init(self):
        rt_region = plane_segmentation.create_roi_table_region(description='the second ROI', region=[1])

        ts = RoiResponseSeries(
            name='test_ts',
            data=list(),
            rois=rt_region,
            unit='unit',
            timestamps=list()
        )

        ff = Fluorescence(ts)
        self.assertEqual(ff.roi_response_series['test_ts'], ts)


class ImageSegmentationConstructor(TestCase):

    def test_init(self, plane_segmentation):
        iS = ImageSegmentation(plane_segmentation, name='test_iS')
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.plane_segmentations[plane_segmentation.name], plane_segmentation)
        self.assertEqual(iS[plane_segmentation.name], iS.plane_segmentations[plane_segmentation.name])


class PlaneSegmentationConstructor(TestCase):

    def test_init(self, imaging_plane, image_series, plane_segmentation):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        plane_segmentation.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        plane_segmentation.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])

        self.assertEqual(plane_segmentation.name, 'test_name')
        self.assertEqual(plane_segmentation.description, 'description')
        self.assertEqual(plane_segmentation.imaging_plane, imaging_plane)
        self.assertEqual(plane_segmentation.reference_images, (image_series,))

        self.assertEqual(plane_segmentation['pixel_mask'].target.data, pix_mask)
        self.assertEqual(plane_segmentation['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(plane_segmentation['pixel_mask'][1], pix_mask[3:5])
        self.assertEqual(plane_segmentation['image_mask'].data, img_mask)

    def test_init_pixel_mask(self, plane_segmentation):
        pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                    [7, 8, 2.0], [9, 10, 2.0]]

        plane_segmentation.add_roi(pixel_mask=pix_mask[0:3])
        plane_segmentation.add_roi(pixel_mask=pix_mask[3:5])

        self.assertEqual(plane_segmentation['pixel_mask'].target.data, pix_mask)
        self.assertEqual(plane_segmentation['pixel_mask'][0], pix_mask[0:3])
        self.assertEqual(plane_segmentation['pixel_mask'][1], pix_mask[3:5])

    def test_init_voxel_mask(self, plane_segmentation):
        vox_mask = [[1, 2, 3, 1.0], [3, 4, 1, 1.0], [5, 6, 3, 1.0],
                    [7, 8, 3, 2.0], [9, 10, 2, 2.0]]

        plane_segmentation.add_roi(voxel_mask=vox_mask[0:3])
        plane_segmentation.add_roi(voxel_mask=vox_mask[3:5])

        self.assertEqual(plane_segmentation['voxel_mask'].target.data, vox_mask)
        self.assertEqual(plane_segmentation['voxel_mask'][0], vox_mask[0:3])
        self.assertEqual(plane_segmentation['voxel_mask'][1], vox_mask[3:5])

    def test_init_image_mask(self, plane_segmentation):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]

        plane_segmentation.add_roi(image_mask=img_mask[0])
        plane_segmentation.add_roi(image_mask=img_mask[1])

        self.assertEqual(plane_segmentation['image_mask'].data, img_mask)

    def test_init_3d_image_mask(self, plane_segmentation):
        img_masks = np.random.randn(2, 20, 30, 4)

        plane_segmentation.add_roi(image_mask=img_masks[0])
        plane_segmentation.add_roi(image_mask=img_masks[1])

        self.assertTrue(np.allclose(plane_segmentation['image_mask'][0], img_masks[0]))
        self.assertTrue(np.allclose(plane_segmentation['image_mask'][1], img_masks[1]))

    def test_conversion_of_2d_pixel_mask_to_image_mask(self, plane_segmentation):
        pixel_mask = [[0, 0, 1.0], [1, 0, 2.0], [2, 0, 2.0]]

        img_mask = plane_segmentation.pixel_to_image(pixel_mask)
        np.testing.assert_allclose(img_mask, np.asarray([[1, 2, 2.0],
                                                         [0, 0, 0.0],
                                                         [0, 0, 0.0]]))

    def test_conversion_of_2d_image_mask_to_pixel_mask(self, plane_segmentation):
        image_mask = np.asarray([[1.0, 0.0, 0.0],
                                 [0.0, 1.0, 0.0],
                                 [0.0, 0.0, 1.0]])

        pixel_mask = plane_segmentation.image_to_pixel(image_mask)
        np.testing.assert_allclose(pixel_mask, np.asarray([[0, 0, 1.0], [1, 1, 1.0], [2, 2, 1.0]]))
