import unittest

from pynwb import TimeSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, EyeTracking, CompassDirection, Position  # noqa: E501


class SpatialSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.source, 'a hypothetical source')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.reference_frame, 'reference_frame')


class BehavioralEpochsConstructor(unittest.TestCase):
    def test_init(self):
        data = [0, 1, 0, 1]
        iS = IntervalSeries('test_iS', 'a hypothetical source', data, timestamps=list())

        bE = BehavioralEpochs('test_bE', iS)
        self.assertEqual(bE.source, 'test_bE')
        self.assertEqual(bE.interval_series['test_iS'], iS)


class BehavioralEventsConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())

        bE = BehavioralEvents('test_bE', ts)
        self.assertEqual(bE.source, 'test_bE')
        self.assertEqual(bE.time_series['test_ts'], ts)


class BehavioralTimeSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())

        bts = BehavioralTimeSeries('test_bts', ts)
        self.assertEqual(bts.source, 'test_bts')
        self.assertEqual(bts.time_series['test_ts'], ts)


class PupilTrackingConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())

        pt = PupilTracking('test_pt', ts)
        self.assertEqual(pt.source, 'test_pt')
        self.assertEqual(pt.timeseries['test_ts'], ts)


class EyeTrackingConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())

        et = EyeTracking('test_et', sS)
        self.assertEqual(et.source, 'test_et')
        self.assertEqual(et.spatial_series['test_sS'], sS)


class CompassDirectionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        cd = CompassDirection('test_cd', sS)
        self.assertEqual(cd.source, 'test_cd')
        self.assertEqual(cd.spatial_series['test_sS'], sS)


class PositionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        pc = Position('test_pc', sS)
        self.assertEqual(pc.source, 'test_pc')
        self.assertEqual(pc.spatial_series.get('test_sS'), sS)


if __name__ == '__main__':
    unittest.main()
