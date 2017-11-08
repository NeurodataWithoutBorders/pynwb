from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder

from pynwb.ophys import (
    ImagingPlane,
    OpticalChannel,
    TwoPhotonSeries
)

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
        nwbfile.set_imaging_plane(self.container)

    def getContainer(self, nwbfile):
        """Should take an NWBFile object and return the Container"""
        return nwbfile.get_imaging_plane(self.container.name)


def make_imaging_plane(self, source):
    self.optical_channel = OpticalChannel('optchan1', source, 'a fake OpticalChannel', '3.14')
    self.imaging_plane = ImagingPlane('imgpln1', source, self.optical_channel,
                                      'a fake ImagingPlane',
                                      'imaging_device_1', '6.28', '2.718', 'GFP', 'somewhere in the brain')


class TestTwoPhotonSeries(base.TestMapRoundTrip):

    def setUpContainer(self):
        make_imaging_plane(self, 'unit test TestTwoPhotonSeries')
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
                'pmt_gain': DatasetBuilder('pmt_gain', 1.7),
                'scan_line_rate': DatasetBuilder('scan_line_rate', 3.4),
            },
            links={
                'imaging_plane': LinkBuilder('imaging_plane', imgpln_builder)
            })

    def addContainer(self, nwbfile):
        """Should take an NWBFile object and add the container to it"""
        nwbfile.set_imaging_plane(self.imaging_plane)
        nwbfile.add_acquisition(self.container)
