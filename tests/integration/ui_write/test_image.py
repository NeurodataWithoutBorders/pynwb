import numpy as np

from pynwb.image import OpticalSeries
from pynwb.testing import TestMapRoundTrip


class TestOpticalSeries(TestMapRoundTrip):

    def setUpContainer(self):
        self.optical_series = OpticalSeries(name='OpticalSeries',
                                            distance=8.,
                                            field_of_view=(4., 5.),
                                            orientation='upper left',
                                            data=np.ones((10, 3, 3)),
                                            unit='m',
                                            format='raw',
                                            timestamps=np.arange(10))
        return self.optical_series

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_stimulus(self.optical_series)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.stimulus['OpticalSeries']
