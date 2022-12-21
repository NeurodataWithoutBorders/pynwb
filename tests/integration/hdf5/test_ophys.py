from abc import ABCMeta
from copy import deepcopy
import numpy as np

from pynwb.ophys import (
    ImagingPlane,
    OpticalChannel,
    PlaneSegmentation,
    ImageSegmentation,
    OnePhotonSeries,
    TwoPhotonSeries,
    RoiResponseSeries,
    MotionCorrection,
    CorrectedImageStack,
)
from pynwb.base import TimeSeries
from pynwb.image import ImageSeries
from pynwb.device import Device
from pynwb.testing import NWBH5IOMixin, AcquisitionH5IOMixin, TestCase


def make_imaging_plane():
    """ Make an ImagingPlane and related objects """
    device = Device(name='dev1')
    optical_channel = OpticalChannel(
        name='optchan1',
        description='a fake OpticalChannel',
        emission_lambda=500.
    )
    imaging_plane = ImagingPlane(
        name='imgpln1',
        optical_channel=optical_channel,
        description='a fake ImagingPlane',
        device=device,
        excitation_lambda=600.,
        imaging_rate=300.,
        indicator='GFP',
        location='somewhere in the brain',
        reference_frame='unknown'
    )

    return device, optical_channel, imaging_plane


class TestImagingPlaneIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test ImagingPlane to read/write """
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel(
            name='optchan1',
            description='a fake OpticalChannel',
            emission_lambda=500.
        )
        return ImagingPlane(
            name='imgpln1',
            optical_channel=self.optical_channel,
            description='a fake ImagingPlane',
            device=self.device,
            excitation_lambda=600.,
            imaging_rate=300.,
            indicator='GFP',
            location='somewhere in the brain',
            reference_frame='unknown',
            origin_coords=[10., 20.],
            origin_coords_unit='millimeters',
            grid_spacing=[0.001, 0.001],
            grid_spacing_unit='millimeters',
        )

    def addContainer(self, nwbfile):
        """ Add the test ImagingPlane and Device to the given NWBFile """
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.container)

    def getContainer(self, nwbfile):
        """ Return the test ImagingPlane from the given NWBFile """
        return nwbfile.get_imaging_plane(self.container.name)


class TestMotionCorrection(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test ImagingPlane to read/write """

        self.device, self.optical_channel, self.imaging_plane = make_imaging_plane()

        self.two_photon_series = TwoPhotonSeries(
            name='TwoPhotonSeries',
            data=np.ones((1000, 100, 100)),
            imaging_plane=self.imaging_plane,
            rate=1.0,
            unit='normalized amplitude'
        )

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

        corrected_image_stack = CorrectedImageStack(
            corrected=corrected,
            original=self.two_photon_series,
            xy_translation=xy_translation,
        )

        return MotionCorrection(corrected_image_stacks=[corrected_image_stack])

    def addContainer(self, nwbfile):
        """ Add the test ImagingPlane and Device to the given NWBFile """

        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.two_photon_series)

        ophys_module = nwbfile.create_processing_module(
            name='ophys',
            description='optical physiology processed data'
        )
        ophys_module.add(self.container)

    def getContainer(self, nwbfile):
        """ Return the test ImagingPlane from the given NWBFile """
        return nwbfile.processing['ophys'].data_interfaces['MotionCorrection']


class TestOnePhotonSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test OnePhotonSeries to read/write """
        self.device, self.optical_channel, self.imaging_plane = make_imaging_plane()
        data = np.ones((10, 2, 2))
        timestamps = list(map(lambda x: x/10, range(10)))
        ret = OnePhotonSeries(
            name='test_2ps',
            imaging_plane=self.imaging_plane,
            data=data,
            unit='image_unit',
            format='raw',
            pmt_gain=1.7,
            scan_line_rate=3.4,
            exposure_time=123.,
            binning=2,
            power=9001.,
            intensity=5.,
            timestamps=timestamps,
            dimension=[2],
        )
        return ret

    def addContainer(self, nwbfile):
        """ Add the test OnePhotonSeries as an acquisition and add Device and ImagingPlane to the given NWBFile """
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)


class TestTwoPhotonSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TwoPhotonSeries to read/write """
        self.device, self.optical_channel, self.imaging_plane = make_imaging_plane()
        data = np.ones((10, 2, 2))
        timestamps = list(map(lambda x: x/10, range(10)))
        fov = [2.0, 2.0, 5.0]
        ret = TwoPhotonSeries(
            name='test_2ps',
            imaging_plane=self.imaging_plane,
            data=data,
            unit='image_unit',
            format='raw',
            field_of_view=fov,
            pmt_gain=1.7,
            scan_line_rate=3.4,
            timestamps=timestamps,
            dimension=[2]
        )
        return ret

    def addContainer(self, nwbfile):
        """ Add the test TwoPhotonSeries as an acquisition and add Device and ImagingPlane to the given NWBFile """
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)


class TestPlaneSegmentationIO(NWBH5IOMixin, TestCase):

    @staticmethod
    def buildPlaneSegmentation(self):
        """ Return an PlaneSegmentation and set related objects """
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [(1, 2, 1.0), (3, 4, 1.0), (5, 6, 1.0),
                    (7, 8, 2.0), (9, 10, 2.)]

        ts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.image_series = ImageSeries(
            name='test_iS',
            dimension=[2],
            external_file=['images.tiff'],
            starting_frame=[0],
            format='external',
            timestamps=ts
        )

        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel(
            name='test_optical_channel',
            description='optical channel description',
            emission_lambda=500.
        )
        self.imaging_plane = ImagingPlane(
            name='imgpln1',
            optical_channel=self.optical_channel,
            description='a fake ImagingPlane',
            device=self.device,
            excitation_lambda=600.,
            imaging_rate=300.,
            indicator='GFP',
            location='somewhere in the brain',
            reference_frame='unknown'
        )

        self.img_mask = deepcopy(img_mask)
        self.pix_mask = deepcopy(pix_mask)
        self.pxmsk_index = [3, 5]
        pS = PlaneSegmentation(
            description='plane segmentation description',
            imaging_plane=self.imaging_plane,
            name='test_plane_seg_name',
            reference_images=self.image_series
        )
        pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])
        return pS

    def setUpContainer(self):
        """ Return the test PlaneSegmentation to read/write """
        return self.buildPlaneSegmentation(self)

    def addContainer(self, nwbfile):
        """
        Add an ImageSegmentation in processing with a PlaneSegmentation and add Device and ImagingPlane to the
        given NWBFile
        """
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.container)
        self.mod = nwbfile.create_processing_module(name='plane_seg_test_module',
                                                    description='a plain module for testing')
        self.mod.add(img_seg)

    def getContainer(self, nwbfile):
        """ Return the test PlaneSegmentation from the given NWBFile """
        mod = nwbfile.get_processing_module(self.mod.name)
        img_seg = mod.get('ImageSegmentation')
        return img_seg.get_plane_segmentation(self.container.name)


class MaskIO(TestPlaneSegmentationIO, metaclass=ABCMeta):

    def buildPlaneSegmentationNoRois(self):
        """ Return an PlaneSegmentation and set related objects """
        ts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.image_series = ImageSeries(
            name='test_iS',
            dimension=[2],
            external_file=['images.tiff'],
            starting_frame=[0],
            format='external',
            timestamps=ts
        )
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel(
            name='test_optical_channel',
            description='optical channel description',
            emission_lambda=500.
        )
        self.imaging_plane = ImagingPlane(
            name='test_imaging_plane',
            optical_channel=self.optical_channel,
            description='imaging plane description',
            device=self.device,
            excitation_lambda=600.,
            imaging_rate=300.,
            indicator='GFP',
            location='somewhere in the brain',
            reference_frame='a frame to refer to'
        )
        return PlaneSegmentation(
            description='description',
            imaging_plane=self.imaging_plane,
            name='test_plane_seg_name',
            reference_images=self.image_series
        )


class TestPixelMaskIO(MaskIO):

    def setUpContainer(self):
        """ Return the test PlaneSegmentation with pixel mask ROIs to read/write """
        pix_mask = [(1, 2, 1.0), (3, 4, 1.0), (5, 6, 1.0),
                    (7, 8, 2.0), (9, 10, 2.)]
        pS = self.buildPlaneSegmentationNoRois()
        pS.add_roi(pixel_mask=pix_mask[0:3])
        pS.add_roi(pixel_mask=pix_mask[3:5])
        return pS


class TestImageMaskIO(MaskIO):

    def setUpContainer(self):
        """ Return the test PlaneSegmentation with voxel mask ROIs to read/write """
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pS = self.buildPlaneSegmentationNoRois()
        pS.add_roi(image_mask=img_mask[0])
        pS.add_roi(image_mask=img_mask[1])
        return pS


class TestRoiResponseSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test RoiResponseSeries to read/write """
        self.plane_segmentation = TestPlaneSegmentationIO.buildPlaneSegmentation(self)
        self.rt_region = self.plane_segmentation.create_roi_table_region('the first of two ROIs', region=[0])

        data = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        return RoiResponseSeries(
            name='test_roi_response_series',
            data=data,
            rois=self.rt_region,
            unit='lumens',
            timestamps=timestamps
        )

    def addContainer(self, nwbfile):
        """
        Add the test RoiResponseSeries as an acquisition and add Device, ImagingPlane, ImageSegmentation, and
        PlaneSegmentation to the given NWBFile
        """
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.plane_segmentation)
        mod = nwbfile.create_processing_module(name='plane_seg_test_module',
                                               description='a plain module for testing')
        mod.add(img_seg)
        super().addContainer(nwbfile)


class TestCorrectedImageStackIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """Return the test CorrectedImageStack to read/write."""
        timestamps = [1., 2.]

        corrected_is = ImageSeries(
            name='corrected',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            timestamps=timestamps
        )
        self.original_is = ImageSeries(
            name='original_is',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            timestamps=timestamps
        )
        tstamps = [1., 2., 3.]
        ts = TimeSeries(
            name='xy_translation',
            data=list(range(len(tstamps))),
            unit='unit',
            timestamps=tstamps
        )
        return CorrectedImageStack(
            corrected=corrected_is,
            original=self.original_is,
            xy_translation=ts
        )

    def addContainer(self, nwbfile):
        """Add the test CorrectedImageStack and the original ImageSeries in acquisition."""
        nwbfile.add_acquisition(self.original_is)
        super().addContainer(nwbfile)
