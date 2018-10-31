import unittest

from pynwb import TimeSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, EyeTracking, CompassDirection, Position  # noqa: E501


class SpatialSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', list(), 'reference_frame', timestamps=list())
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.reference_frame, 'reference_frame')


class BehavioralEpochsConstructor(unittest.TestCase):
    def test_init(self):
        data = [0, 1, 0, 1]
        iS = IntervalSeries('test_iS', data, timestamps=list())

        bE = BehavioralEpochs(iS)
        self.assertEqual(bE.interval_series['test_iS'], iS)


class BehavioralEventsConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())

        bE = BehavioralEvents(ts)
        self.assertEqual(bE.time_series['test_ts'], ts)


class BehavioralTimeSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())

        bts = BehavioralTimeSeries(ts)
        self.assertEqual(bts.time_series['test_ts'], ts)


class PupilTrackingConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())

        pt = PupilTracking(ts)
        self.assertEqual(pt.time_series['test_ts'], ts)


class EyeTrackingConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', list(), 'reference_frame', timestamps=list())

        et = EyeTracking(sS)
        self.assertEqual(et.spatial_series['test_sS'], sS)


class CompassDirectionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', list(), 'reference_frame', timestamps=list())

        cd = CompassDirection(sS)
        self.assertEqual(cd.spatial_series['test_sS'], sS)


class PositionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', list(), 'reference_frame', timestamps=list())

        pc = Position(sS)
        self.assertEqual(pc.spatial_series.get('test_sS'), sS)


if __name__ == '__main__':
    unittest.main()
