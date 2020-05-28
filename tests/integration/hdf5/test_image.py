import numpy as np

from pynwb.image import OpticalSeries
from pynwb.testing import NWBH5IOMixin, TestCase


class TestOpticalSeriesIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return a test OpticalSeries to read/write """
        self.optical_series = OpticalSeries(name='OpticalSeries',
                                            distance=8.,
                                            field_of_view=(4., 5.),
                                            orientation='upper left',
                                            data=np.ones((10, 3, 3)),
                                            unit='m',
                                            format='raw',
                                            timestamps=np.arange(10.))
        return self.optical_series

    def addContainer(self, nwbfile):
        """ Add the test OpticalSeries to the given NWBFile """
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        """ Return the test OpticalSeries from the given NWBFile """
        return nwbfile.stimulus['OpticalSeries']
