from copy import deepcopy

from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder, RegionBuilder

from pynwb.ophys import (
    ImagingPlane,
    OpticalChannel,
    PlaneSegmentation,
    ImageSegmentation,
    TwoPhotonSeries
)

from pynwb.image import ImageSeries

from . import base


class TestImagingPlaneIO(base.TestMapRoundTrip):
    """
    A TestCase class for testing ImagingPlane
    """

    def setUpContainer(self):
        self.optical_channel = OpticalChannel('optchan1', 'unit test TestImagingPlaneIO',
                                              'a fake OpticalChannel', '3.14')
        return ImagingPlane('imgpln1', 'unit test TestImagingPlaneIO', self.optical_channel,
                            'a fake ImagingPlane', 'imaging_device_1', '6.28', '2.718', 'GFP', 'somewhere in the brain')

    def setUpBuilder(self):
        optchan_builder = GroupBuilder(
            'optchan1',
            attributes={
                'neurodata_type': 'OpticalChannel',
                'namespace': 'core',
                'help': 'Metadata about an optical channel used to record from an imaging plane',
                'source': 'unit test TestImagingPlaneIO'},
            datasets={
                'description': DatasetBuilder('description', 'a fake OpticalChannel'),
                'emission_lambda': DatasetBuilder('emission_lambda', '3.14')},
        )
        return GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'source': 'unit test TestImagingPlaneIO',
                'help': 'Metadata about an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'a fake ImagingPlane'),
                'device': DatasetBuilder('device', 'imaging_device_1'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', '6.28'),
                'imaging_rate': DatasetBuilder('imaging_rate', '2.718'),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': optchan_builder
            }
        )

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_imaging_plane(self.container)

    def getContainer(self, nwbfile):
        """Should take an NWBFile object and return the Container"""
        return nwbfile.get_imaging_plane(self.container.name)


class TestTwoPhotonSeries(base.TestDataInterfaceIO):

    def make_imaging_plane(self, source):
        self.optical_channel = OpticalChannel('optchan1', source, 'a fake OpticalChannel', '3.14')
        self.imaging_plane = ImagingPlane('imgpln1', source, self.optical_channel,
                                          'a fake ImagingPlane',
                                          'imaging_device_1', '6.28', '2.718', 'GFP', 'somewhere in the brain')

    def setUpContainer(self):
        self.make_imaging_plane('unit test TestTwoPhotonSeries')
        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        fov = [2.0, 2.0, 5.0]
        ret = TwoPhotonSeries('test_2ps', 'unit test TestTwoPhotonSeries',
                              data, self.imaging_plane, 'image_unit', 'raw', fov, 1.7, 3.4,
                              timestamps=timestamps, dimension=[2])
        return ret

    def setUpBuilder(self):
        optchan_builder = GroupBuilder(
            'optchan1',
            attributes={
                 'neurodata_type': 'OpticalChannel',
                 'namespace': 'core',
                 'help': 'Metadata about an optical channel used to record from an imaging plane',
                 'source': 'unit test TestTwoPhotonSeries'},
            datasets={
                 'description': DatasetBuilder('description', 'a fake OpticalChannel'),
                 'emission_lambda': DatasetBuilder('emission_lambda', '3.14')},
        )
        imgpln_builder = GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'help': 'Metadata about an imaging plane',
                'source': 'unit test TestTwoPhotonSeries'},
            datasets={
                'description': DatasetBuilder('description', 'a fake ImagingPlane'),
                'device': DatasetBuilder('device', 'imaging_device_1'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', '6.28'),
                'imaging_rate': DatasetBuilder('imaging_rate', '2.718'),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': optchan_builder
            }
        )

        data = list(zip(range(10), range(10, 20)))
        timestamps = list(map(lambda x: x/10, range(10)))
        return GroupBuilder(
            'test_2ps',
            attributes={
                'source': 'unit test TestTwoPhotonSeries',
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
                'imaging_plane': LinkBuilder('imaging_plane', imgpln_builder)
            })

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.add_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)


class TestPlaneSegmentation(base.TestMapRoundTrip):

    @staticmethod
    def buildPlaneSegmentation(self):
        w, h = 5, 5
        img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
        pix_mask = [(1, 2, 1.0), (3, 4, 1.0), (5, 6, 1.0),
                    (7, 8, 2.0), (9, 10, 2.)]

        self.image_series = ImageSeries(name='test_iS', source='a hypothetical source', dimension=[2],
                                        external_file=['images.tiff'],
                                        starting_frame=[1, 2, 3], format='tiff', timestamps=list())

        self.optical_channel = OpticalChannel('test_optical_channel', 'optical channel source',
                                              'optical channel description', '3.14')
        self.imaging_plane = ImagingPlane('test_imaging_plane',
                                          'ophys integration tests',
                                          self.optical_channel,
                                          'imaging plane description',
                                          'imaging_device_1',
                                          '6.28', '2.718', 'GFP', 'somewhere in the brain',
                                          (1, 2, 1, 2, 3), 4.0, 'manifold unit', 'A frame to refer to')

        self.img_mask = deepcopy(img_mask)
        self.pix_mask = deepcopy(pix_mask)
        pS = PlaneSegmentation('integration test PlaneSegmentation', 'plane segmentation description',
                               self.imaging_plane, 'test_plane_seg_name', self.image_series)
        pS.add_roi(pix_mask[0:3], img_mask[0])
        pS.add_roi(pix_mask[3:5], img_mask[1])
        return pS

    @staticmethod
    def get_plane_segmentation_builder(self):
        self.optchan_builder = GroupBuilder(
            'test_optical_channel',
            attributes={
                'neurodata_type': 'OpticalChannel',
                'namespace': 'core',
                'help': 'Metadata about an optical channel used to record from an imaging plane',
                'source': 'optical channel source'},
            datasets={
                'description': DatasetBuilder('description', 'optical channel description'),
                'emission_lambda': DatasetBuilder('emission_lambda', '3.14')},
        )
        self.imgpln_builder = GroupBuilder(
            'imgpln1',
            attributes={
                'neurodata_type': 'ImagingPlane',
                'namespace': 'core',
                'source': 'ophys integration tests',
                'help': 'Metadata about an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'imaging plane description'),
                'device': DatasetBuilder('device', 'imaging_device_1'),
                'excitation_lambda': DatasetBuilder('excitation_lambda', '6.28'),
                'imaging_rate': DatasetBuilder('imaging_rate', '2.718'),
                'indicator': DatasetBuilder('indicator', 'GFP'),
                'manifold': DatasetBuilder('manifold', (1, 2, 1, 2, 3),
                                           attributes={'conversion': 4.0, 'unit': 'manifold unit'}),
                'reference_frame': DatasetBuilder('reference_frame', 'A frame to refer to'),
                'location': DatasetBuilder('location', 'somewhere in the brain')},
            groups={
                'optchan1': self.optchan_builder
            }
        )
        self.is_builder = GroupBuilder('test_iS',
                                       attributes={'source': 'a hypothetical source',
                                                   'namespace': 'core',
                                                   'neurodata_type': 'ImageSeries',
                                                   'description': 'no description',
                                                   'comments': 'no comments',
                                                   'help': 'Storage object for time-series 2-D image data'},
                                       datasets={'timestamps': DatasetBuilder('timestamps', [],
                                                                              attributes={'unit': 'Seconds',
                                                                                          'interval': 1}),
                                                 'external_file': DatasetBuilder('external_file', ['images.tiff'],
                                                                                 attributes={
                                                                                    'starting_frame': [1, 2, 3]}),
                                                 'format': DatasetBuilder('format', 'tiff'),
                                                 'dimension': DatasetBuilder('dimension', [2]),
                                                 })

        self.pixel_masks_builder = DatasetBuilder('pixel_masks', self.pix_mask,
                                                  attributes={
                                                   'namespace': 'core',
                                                   'neurodata_type': 'PixelMasks',
                                                   'help': 'a concatenated array of pixel masks'})

        self.image_masks_builder = DatasetBuilder('image_masks', self.img_mask,
                                                  attributes={
                                                   'namespace': 'core',
                                                   'neurodata_type': 'ImageMasks',
                                                   'help': 'an array of image masks'})

        self.rois_builder = DatasetBuilder('rois', [
                                            (RegionBuilder(slice(0, 3), self.pixel_masks_builder),
                                             RegionBuilder([0], self.image_masks_builder)),
                                            (RegionBuilder(slice(3, 5), self.pixel_masks_builder),
                                             RegionBuilder([1], self.image_masks_builder))
                                        ],
                                        attributes={
                                         'namespace': 'core',
                                         'neurodata_type': 'ROITable',
                                         'help': 'A table for storing ROI data'})
        ps_builder = GroupBuilder(
            'test_plane_seg_name',
            attributes={
                'neurodata_type': 'PlaneSegmentation',
                'namespace': 'core',
                'source': 'integration test PlaneSegmentation',
                'help': 'Results from segmentation of an imaging plane'},
            datasets={
                'description': DatasetBuilder('description', 'plane segmentation description'),
                'rois': self.rois_builder,
                'pixel_masks': self.pixel_masks_builder,
                'image_masks': self.image_masks_builder,
            },
            groups={
                'reference_images': GroupBuilder('reference_images', groups={'test_iS': self.is_builder}),
            },
            links={
                'imaging_plane': LinkBuilder('imaging_plane', self.imgpln_builder)
            }
        )
        return ps_builder

    def setUpContainer(self):
        return self.buildPlaneSegmentation(self)

    def setUpBuilder(self):
        return self.get_plane_segmentation_builder(self)

    def addContainer(self, nwbfile):
        nwbfile.add_imaging_plane(self.imaging_plane)
        img_seg = ImageSegmentation('plane segmentation round trip')
        img_seg.add_plane_segmentation(self.container)
        mod = nwbfile.create_processing_module('plane_seg_test_module',
                                               'plane segmentation round trip',
                                               'a plain module for testing')
        mod.add_data_interface(img_seg)

    def getContainer(self, nwbfile):
        mod = nwbfile.get_processing_module('plane_seg_test_module')
        img_seg = mod.get_container('ImageSegmentation')
        return img_seg.get_plane_segmentation('test_plane_seg_name')
