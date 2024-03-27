import numpy as np

from pynwb import TimeSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import (SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking,
                            EyeTracking, CompassDirection, Position)
from pynwb.testing import TestCase


class SpatialSeriesConstructor(TestCase):
    def test_init(self):
        sS = SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            bounds=[(-1,1),(-1,1),(-1,1)],
            reference_frame='reference_frame',
            timestamps=[1., 2., 3.]
        )
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.bounds, [(-1,1),(-1,1),(-1,1)])
        self.assertEqual(sS.reference_frame, 'reference_frame')

    def test_set_unit(self):
        sS = SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            reference_frame='reference_frame',
            unit='degrees',
            timestamps=[1., 2., 3.]
        )
        self.assertEqual(sS.unit, 'degrees')

    def test_gt_3_cols(self):
        msg = ("SpatialSeries 'test_sS' has data shape (5, 4) which is not compliant with NWB 2.5 and greater. "
               "The second dimension should have length <= 3 to represent at most x, y, z.")
        with self.assertWarnsWith(UserWarning, msg):
            SpatialSeries(
                name="test_sS",
                data=np.ones((5, 4)),
                reference_frame="reference_frame",
                rate=30.
            )


class BehavioralEpochsConstructor(TestCase):
    def test_init(self):
        data = [0, 1, 0]
        iS = IntervalSeries(name='test_iS', data=data, timestamps=[1., 2., 3.])

        bE = BehavioralEpochs(iS)
        self.assertEqual(bE.interval_series['test_iS'], iS)


class BehavioralEventsConstructor(TestCase):
    def test_init(self):
        ts = TimeSeries(name='test_ts', data=np.ones((3, 2)), unit='unit', timestamps=[1., 2., 3.])

        bE = BehavioralEvents(ts)
        self.assertEqual(bE.time_series['test_ts'], ts)


class BehavioralTimeSeriesConstructor(TestCase):
    def test_init(self):
        ts = TimeSeries(name='test_ts', data=np.ones((3, 2)), unit='unit', timestamps=[1., 2., 3.])

        bts = BehavioralTimeSeries(ts)
        self.assertEqual(bts.time_series['test_ts'], ts)


class PupilTrackingConstructor(TestCase):
    def test_init(self):
        ts = TimeSeries(name='test_ts', data=np.ones((3, 2)), unit='unit', timestamps=[1., 2., 3.])

        pt = PupilTracking(ts)
        self.assertEqual(pt.time_series['test_ts'], ts)


class EyeTrackingConstructor(TestCase):
    def test_init(self):
        sS = SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            reference_frame='reference_frame',
            timestamps=[1., 2., 3.]
        )

        et = EyeTracking(sS)
        self.assertEqual(et.spatial_series['test_sS'], sS)


class CompassDirectionConstructor(TestCase):
    def test_init(self):
        sS = SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            reference_frame='reference_frame',
            timestamps=[1., 2., 3.]
        )

        cd = CompassDirection(sS)
        self.assertEqual(cd.spatial_series['test_sS'], sS)


class PositionConstructor(TestCase):
    def test_init(self):
        sS = SpatialSeries(
            name='test_sS',
            data=np.ones((3, 2)),
            reference_frame='reference_frame',
            timestamps=[1., 2., 3.]
        )

        pc = Position(sS)
        self.assertEqual(pc.spatial_series.get('test_sS'), sS)
