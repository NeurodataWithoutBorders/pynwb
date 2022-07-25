import numpy as np

from pynwb.device import Device
from pynwb.image import ImageSeries, OpticalSeries
from pynwb.testing import AcquisitionH5IOMixin, NWBH5IOMixin, TestCase


class TestImageSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test ImageSeries to read/write """
        self.dev1 = Device('dev1')
        iS = ImageSeries(
            name='test_iS',
            unit='unit',
            external_file=['external_file'],
            starting_frame=[0],
            format='external',
            timestamps=[1., 2., 3.],
            device=self.dev1,
        )
        return iS

    def addContainer(self, nwbfile):
        """ Add the test ElectrodeGroup to the given NWBFile """
        nwbfile.add_device(self.dev1)
        super().addContainer(nwbfile)


class TestOpticalSeriesIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test OpticalSeries to read/write """
        self.dev1 = Device('dev1')
        self.optical_series = OpticalSeries(
            name='OpticalSeries',
            distance=8.,
            field_of_view=(4., 5.),
            orientation='upper left',
            data=np.ones((10, 3, 3)),
            unit='m',
            format='raw',
            timestamps=np.arange(10.),
            device=self.dev1,
        )
        return self.optical_series

    def addContainer(self, nwbfile):
        """ Add the test OpticalSeries to the given NWBFile """
        nwbfile.add_device(self.dev1)
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        """ Return the test OpticalSeries from the given NWBFile """
        return nwbfile.stimulus['OpticalSeries']
