import numpy as np

from pynwb.behavior import SpatialSeries
from pynwb.testing import AcquisitionH5IOMixin, TestCase


class TestSpatialSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TimeSeries to read/write """
        return SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            reference_frame='reference_frame',
            timestamps=[1., 2., 3.]
        )


class TestSpatialSeriesMinIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TimeSeries to read/write """
        return SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            timestamps=[1., 2., 3.]
        )
