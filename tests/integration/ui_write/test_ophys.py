from copy import deepcopy

from pynwb.ophys import (
    ImagingPlane,
    OpticalChannel,
    PlaneSegmentation,
    ImageSegmentation,
    TwoPhotonSeries,
    RoiResponseSeries
)
from pynwb.image import ImageSeries
from pynwb.device import Device
from pynwb.testing import TestMapRoundTrip, TestDataInterfaceIO


class TestImagingPlaneIO(TestMapRoundTrip):
    """
    A TestCase class for testing ImagingPlane
    """

    def setUpContainer(self):
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('optchan1',
                                              'a fake OpticalChannel', 500.)
        return ImagingPlane('imgpln1', self.optical_channel, 'a fake ImagingPlane', self.device,
                            600., 300., 'GFP', 'somewhere in the brain', reference_frame='unknonwn')

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.container)

    def getContainer(self, nwbfile):
        """Should take an NWBFile object and return the Container"""
        return nwbfile.get_imaging_plane(self.container.name)


class TestTwoPhotonSeries(TestDataInterfaceIO):

    def make_imaging_plane(self):
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('optchan1', 'a fake OpticalChannel', 500.)
        self.imaging_plane = ImagingPlane('imgpln1', self.optical_channel, 'a fake ImagingPlane', self.device,
                                          600., 300., 'GFP', 'somewhere in the brain', reference_frame='unknown')

    def setUpContainer(self):
        self.make_imaging_plane()
        data = [[[1., 1.] * 2] * 2]
        timestamps = list(map(lambda x: x/10, range(10)))
        fov = [2.0, 2.0, 5.0]
        ret = TwoPhotonSeries('test_2ps', self.imaging_plane, data, 'image_unit', 'raw', fov, 1.7, 3.4,
                              timestamps=timestamps, dimension=[2])
        return ret

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)


class TestPlaneSegmentation(TestMapRoundTrip):

    @staticmethod
    def buildPlaneSegmentation(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [(1, 2, 1.0), (3, 4, 1.0), (5, 6, 1.0),
                    (7, 8, 2.0), (9, 10, 2.)]

        ts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.image_series = ImageSeries(name='test_iS', dimension=[2],
                                        external_file=['images.tiff'],
                                        starting_frame=[1, 2, 3], format='tiff', timestamps=ts)

        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('test_optical_channel',
                                              'optical channel description', 500.)
        self.imaging_plane = ImagingPlane('imgpln1',
                                          self.optical_channel,
                                          'a fake ImagingPlane',
                                          self.device,
                                          600., 200., 'GFP', 'somewhere in the brain',
                                          (((1., 2., 3.), (4., 5., 6.)),),
                                          2., 'a unit',
                                          reference_frame='unknown')

        self.img_mask = deepcopy(img_mask)
        self.pix_mask = deepcopy(pix_mask)
        self.pxmsk_index = [3, 5]
        pS = PlaneSegmentation('plane segmentation description',
                               self.imaging_plane, 'test_plane_seg_name', self.image_series)
        pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])
        return pS

    def setUpContainer(self):
        return self.buildPlaneSegmentation(self)

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.container)
        mod = nwbfile.create_processing_module('plane_seg_test_module',
                                               'a plain module for testing')
        mod.add(img_seg)

    def getContainer(self, nwbfile):
        mod = nwbfile.get_processing_module('plane_seg_test_module')
        img_seg = mod.get('ImageSegmentation')
        return img_seg.get_plane_segmentation('test_plane_seg_name')


class MaskRoundTrip(TestPlaneSegmentation):

    def setBoilerPlateObjects(self):
        ts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.image_series = ImageSeries(name='test_iS', dimension=[2],
                                        external_file=['images.tiff'],
                                        starting_frame=[1, 2, 3], format='tiff', timestamps=ts)
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('test_optical_channel',
                                              'optical channel description', 500.)
        self.imaging_plane = ImagingPlane('test_imaging_plane',
                                          self.optical_channel,
                                          'imaging plane description',
                                          self.device,
                                          600., 300., 'GFP', 'somewhere in the brain',
                                          (((1., 2., 3.), (4., 5., 6.)),),
                                          4.0, 'manifold unit', 'A frame to refer to')
        return PlaneSegmentation('description', self.imaging_plane, 'test_plane_seg_name',
                                 self.image_series)


class PixelMaskRoundtrip(MaskRoundTrip):

    def setUpContainer(self):
        pix_mask = [(1, 2, 1.0), (3, 4, 1.0), (5, 6, 1.0),
                    (7, 8, 2.0), (9, 10, 2.)]
        pS = self.setBoilerPlateObjects()
        pS.add_roi(pixel_mask=pix_mask[0:3])
        pS.add_roi(pixel_mask=pix_mask[3:5])
        return pS


class ImageMaskRoundtrip(MaskRoundTrip):

    def setUpContainer(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pS = self.setBoilerPlateObjects()
        pS.add_roi(image_mask=img_mask[0])
        pS.add_roi(image_mask=img_mask[1])
        return pS


class TestRoiResponseSeriesIO(TestDataInterfaceIO):

    def setUpContainer(self):
        self.plane_segmentation = TestPlaneSegmentation.buildPlaneSegmentation(self)
        self.rt_region = self.plane_segmentation.create_roi_table_region('the first of two ROIs', region=[0])

        data = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        return RoiResponseSeries('test_roi_response_series', data, self.rt_region, unit='lumens',
                                 timestamps=timestamps)

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.plane_segmentation)
        mod = nwbfile.create_processing_module('plane_seg_test_module',
                                               'a plain module for testing')
        mod.add(img_seg)
        super(TestRoiResponseSeriesIO, self).addContainer(nwbfile)
