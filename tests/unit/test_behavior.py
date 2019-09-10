import unittest

import numpy as np

from pynwb import TimeSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, \
                           EyeTracking, CompassDirection, Position


class SpatialSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', np.ones((2, 2)), 'reference_frame', timestamps=[1., 2., 3.])
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.reference_frame, 'reference_frame')


class BehavioralEpochsConstructor(unittest.TestCase):
    def test_init(self):
        data = [0, 1, 0, 1]
        iS = IntervalSeries('test_iS', data, timestamps=[1., 2., 3.])

        bE = BehavioralEpochs(iS)
        self.assertEqual(bE.interval_series['test_iS'], iS)


class BehavioralEventsConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', np.ones((2, 2)), 'unit', timestamps=[1., 2., 3.])

        bE = BehavioralEvents(ts)
        self.assertEqual(bE.time_series['test_ts'], ts)


class BehavioralTimeSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', np.ones((2, 2)), 'unit', timestamps=[1., 2., 3.])

        bts = BehavioralTimeSeries(ts)
        self.assertEqual(bts.time_series['test_ts'], ts)


class PupilTrackingConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', np.ones((2, 2)), 'unit', timestamps=[1., 2., 3.])

        pt = PupilTracking(ts)
        self.assertEqual(pt.time_series['test_ts'], ts)


class EyeTrackingConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', np.ones((2, 2)), 'reference_frame', timestamps=[1., 2., 3.])

        et = EyeTracking(sS)
        self.assertEqual(et.spatial_series['test_sS'], sS)


class CompassDirectionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', np.ones((2, 2)), 'reference_frame', timestamps=[1., 2., 3.])

        cd = CompassDirection(sS)
        self.assertEqual(cd.spatial_series['test_sS'], sS)


class PositionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', np.ones((2, 2)), 'reference_frame', timestamps=[1., 2., 3.])

        pc = Position(sS)
        self.assertEqual(pc.spatial_series.get('test_sS'), sS)


if __name__ == '__main__':
    unittest.main()
