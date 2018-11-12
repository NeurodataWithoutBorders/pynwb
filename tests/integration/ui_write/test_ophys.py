import unittest2 as unittest
from copy import deepcopy

from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, ReferenceBuilder

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

from . import base


class TestImagingPlaneIO(base.TestMapRoundTrip):
    """
    A TestCase class for testing ImagingPlane
    """

    def setUpContainer(self):
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('optchan1',
                                              'a fake OpticalChannel', 500.)
        return ImagingPlane('imgpln1', self.optical_channel,
                            'a fake ImagingPlane', self.device, 600., 300., 'GFP', 'somewhere in the brain')

    def setUpBuilder(self):
        optchan_builder = GroupBuilder(
            'optchan1',
            attributes={
                'neurodata_type': 'OpticalChannel',
                'namespace': 'core',
                'help': 'Metadata about an optical channel used to record from an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'a fake OpticalChannel'),
                'emission_lambda': DatasetBuilder('emission_lambda', 500.)},
        )
        device_builder = GroupBuilder('dev1',
                                      attributes={'neurodata_type': 'Device',
                                                  'namespace': 'core',
                                                  'help': 'A recording device e.g. amplifier'})
        return GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'help': 'Metadata about an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'a fake ImagingPlane'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', 600.),
                'imaging_rate': DatasetBuilder('imaging_rate', 300.),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': optchan_builder
            },
            links={
                'device': LinkBuilder(device_builder, 'device')
            }
        )

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.container)

    def getContainer(self, nwbfile):
        """Should take an NWBFile object and return the Container"""
        return nwbfile.get_imaging_plane(self.container.name)


class TestTwoPhotonSeries(base.TestDataInterfaceIO):

    def make_imaging_plane(self):
        self.device = Device(name='dev1')
        self.optical_channel = OpticalChannel('optchan1', 'a fake OpticalChannel', 500.)
        self.imaging_plane = ImagingPlane('imgpln1', self.optical_channel,
                                          'a fake ImagingPlane',
                                          self.device, 600., 300., 'GFP', 'somewhere in the brain')

    def setUpContainer(self):
        self.make_imaging_plane()
        data = [[[1., 1.] * 2] * 2]
        timestamps = list(map(lambda x: x/10, range(10)))
        fov = [2.0, 2.0, 5.0]
        ret = TwoPhotonSeries('test_2ps', self.imaging_plane, data, 'image_unit', 'raw', fov, 1.7, 3.4,
                              timestamps=timestamps, dimension=[2])
        return ret

    def setUpBuilder(self):
        optchan_builder = GroupBuilder(
            'optchan1',
            attributes={
                 'neurodata_type': 'OpticalChannel',
                 'namespace': 'core',
                 'help': 'Metadata about an optical channel used to record from an imaging plane'},
            datasets={
                 'description': DatasetBuilder('description', 'a fake OpticalChannel'),
                 'emission_lambda': DatasetBuilder('emission_lambda', 500.)},
        )
        device_builder = GroupBuilder('dev1',
                                      attributes={'neurodata_type': 'Device',
                                                  'namespace': 'core',
                                                  'help': 'A recording device e.g. amplifier'})
        imgpln_builder = GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'help': 'Metadata about an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'a fake ImagingPlane'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', 600.),
                'imaging_rate': DatasetBuilder('imaging_rate', 300.),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': optchan_builder
            },
            links={
                'device': LinkBuilder(device_builder, 'device')
            }
        )

        data = [[[1., 1.] * 2] * 2]
        timestamps = list(map(lambda x: x/10, range(10)))
        return GroupBuilder(
            'test_2ps',
            attributes={
                'pmt_gain':  1.7,
                'scan_line_rate':  3.4,
                'namespace': base.CORE_NAMESPACE,
                'comments': 'no comments',
                'description': 'no description',
                'neurodata_type': 'TwoPhotonSeries',
                'help': 'Image stack recorded from 2-photon microscope'},
            datasets={
                'data': DatasetBuilder(
                    'data', data,
                    attributes={
                        'unit': 'image_unit',
                        'conversion': 1.0,
                        'resolution': 0.0}
                ),
                'timestamps': DatasetBuilder('timestamps', timestamps,
                                             attributes={'unit': 'Seconds', 'interval': 1}),
                'format': DatasetBuilder('format', 'raw'),
                'dimension': DatasetBuilder('dimension', [2]),
                'field_of_view': DatasetBuilder('field_of_view', [2.0, 2.0, 5.0]),
            },
            links={
                'imaging_plane': LinkBuilder(imgpln_builder, 'imaging_plane')
            })

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)


class TestPlaneSegmentation(base.TestMapRoundTrip):

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
        self.imaging_plane = ImagingPlane('ophys integration tests',
                                          self.optical_channel,
                                          'imaging plane description',
                                          self.device,
                                          600., 300., 'GFP', 'somewhere in the brain',
                                          (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')

        self.img_mask = deepcopy(img_mask)
        self.pix_mask = deepcopy(pix_mask)
        self.pxmsk_index = [3, 5]
        pS = PlaneSegmentation('plane segmentation description',
                               self.imaging_plane, 'test_plane_seg_name', self.image_series)
        pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
        pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])
        return pS

    @staticmethod
    def get_plane_segmentation_builder(self):
        self.optchan_builder = GroupBuilder(
            'test_optical_channel',
            attributes={
                'neurodata_type': 'OpticalChannel',
                'namespace': 'core',
                'help': 'Metadata about an optical channel used to record from an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'optical channel description'),
                'emission_lambda': DatasetBuilder('emission_lambda', 500.)},
        )
        device_builder = GroupBuilder('dev1',
                                      attributes={'neurodata_type': 'Device',
                                                  'namespace': 'core',
                                                  'help': 'A recording device e.g. amplifier'})
        self.imgpln_builder = GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'help': 'Metadata about an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'imaging plane description'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', 600.),
                'imaging_rate': DatasetBuilder('imaging_rate', 300.),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'manifold': DatasetBuilder('manifold', (1, 2, 1, 2, 3),
                                           attributes={'conversion': 4.0, 'unit': 'manifold unit'}),
                'reference_frame': DatasetBuilder('reference_frame', 'A frame to refer to'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': self.optchan_builder
            },
            links={
                'device': LinkBuilder(device_builder, 'device')
            }
        )
        ts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.is_builder = GroupBuilder('test_iS',
                                       attributes={'namespace': 'core',
                                                   'neurodata_type': 'ImageSeries',
                                                   'description': 'no description',
                                                   'comments': 'no comments',
                                                   'help': 'Storage object for time-series 2-D image data'},
                                       datasets={'timestamps': DatasetBuilder('timestamps', ts,
                                                                              attributes={'unit': 'Seconds',
                                                                                          'interval': 1}),
                                                 'external_file': DatasetBuilder('external_file', ['images.tiff'],
                                                                                 attributes={
                                                                                    'starting_frame': [1, 2, 3]}),
                                                 'format': DatasetBuilder('format', 'tiff'),
                                                 'dimension': DatasetBuilder('dimension', [2]),
                                                 })

        self.pixel_masks_builder = DatasetBuilder('pixel_mask', self.pix_mask,
                                                  attributes={
                                                   'namespace': 'core',
                                                   'neurodata_type': 'VectorData',
                                                   'description': 'Pixel masks for each ROI',
                                                   'help': 'Values for a list of elements'})

        self.pxmsk_index_builder = DatasetBuilder('pixel_mask_index', self.pxmsk_index,
                                                  attributes={
                                                   'namespace': 'core',
                                                   'neurodata_type': 'VectorIndex',
                                                   'target': ReferenceBuilder(self.pixel_masks_builder),
                                                   'help': 'indexes into a list of values for a list of elements'})

        self.image_masks_builder = DatasetBuilder('image_mask', self.img_mask,
                                                  attributes={
                                                   'namespace': 'core',
                                                   'neurodata_type': 'VectorData',
                                                   'description': 'Image masks for each ROI',
                                                   'help': 'Values for a list of elements'})

        ps_builder = GroupBuilder(
            'test_plane_seg_name',
            attributes={
                'neurodata_type': 'PlaneSegmentation',
                'namespace': 'core',
                'description': 'plane segmentation description',
                'colnames': ('image_mask', 'pixel_mask'),
                'help': 'Results from segmentation of an imaging plane'},
            datasets={
                'id': DatasetBuilder('id', data=[0, 1],
                                     attributes={'help': 'unique identifiers for a list of elements',
                                                 'namespace': 'core',
                                                 'neurodata_type': 'ElementIdentifiers'}),
                'pixel_mask': self.pixel_masks_builder,
                'pixel_mask_index': self.pxmsk_index_builder,
                'image_mask': self.image_masks_builder,
            },
            groups={
                'reference_images': GroupBuilder('reference_images', groups={'test_iS': self.is_builder}),
            },
            links={
                'imaging_plane': LinkBuilder(self.imgpln_builder, 'imaging_plane')
            }
        )
        return ps_builder

    def setUpContainer(self):
        return self.buildPlaneSegmentation(self)

    def setUpBuilder(self):
        return self.get_plane_segmentation_builder(self)

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.container)
        mod = nwbfile.create_processing_module('plane_seg_test_module',
                                               'a plain module for testing')
        mod.add_data_interface(img_seg)

    def getContainer(self, nwbfile):
        mod = nwbfile.get_processing_module('plane_seg_test_module')
        img_seg = mod.get_data_interface('ImageSegmentation')
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
                                          (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')
        return PlaneSegmentation('description', self.imaging_plane, 'test_plane_seg_name',
                                 self.image_series)

    def setUpBuilder(self):
        raise unittest.SkipTest("no builder")


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


class TestRoiResponseSeriesIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        self.plane_segmentation = TestPlaneSegmentation.buildPlaneSegmentation(self)
        self.rt_region = self.plane_segmentation.create_roi_table_region('the first of two ROIs', region=[0])

        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        return RoiResponseSeries('test_roi_response_series', data, 'lumens', self.rt_region, timestamps=timestamps)

    def setUpBuilder(self):
        ps_builder = TestPlaneSegmentation.get_plane_segmentation_builder(self)
        return GroupBuilder(
            'test_roi_response_series',
            attributes={
                'namespace': base.CORE_NAMESPACE,
                'comments': 'no comments',
                'description': 'no description',
                'neurodata_type': 'RoiResponseSeries',
                'help': ('ROI responses over an imaging plane. Each element on the second dimension of data[] '
                         'should correspond to the signal from one ROI')},
            datasets={
                'data': DatasetBuilder(
                    'data', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    attributes={
                        'unit': 'lumens',
                        'conversion': 1.0,
                        'resolution': 0.0}
                ),
                'timestamps': DatasetBuilder('timestamps', [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                                             attributes={'unit': 'Seconds', 'interval': 1}),
                'rois': DatasetBuilder('rois', data=[0],
                                       attributes={'help': 'a subset (i.e. slice or region) of a DynamicTable',
                                                   'description': 'the first of two ROIs',
                                                   'table': ReferenceBuilder(ps_builder),
                                                   'namespace': 'core',
                                                   'neurodata_type': 'DynamicTableRegion'}),
            })

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation()
        img_seg.add_plane_segmentation(self.plane_segmentation)
        mod = nwbfile.create_processing_module('plane_seg_test_module',
                                               'a plain module for testing')
        mod.add_data_interface(img_seg)
        super(TestRoiResponseSeriesIO, self).addContainer(nwbfile)
