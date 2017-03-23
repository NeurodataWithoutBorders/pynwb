import unittest

from pynwb import TimeSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, EyeTracking, CompassDirection, Position, MotionCorrection

import numpy as np


class SpatialSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.source, 'a hypothetical source')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.reference_frame, 'reference_frame')

class BehavioralEpochsConstructor(unittest.TestCase):
    def test_init(self):
        iS = IntervalSeries('test_iS', 'a hypothetical source')
        bE = BehavioralEpochs('test_bE', iS)
        self.assertEqual(bE.source, 'test_bE')
        self.assertEqual(bE._IntervalSeries, iS)

class BehavioralEventsConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        bE = BehavioralEvents('test_bE', ts)
        self.assertEqual(bE.source, 'test_bE')
        self.assertEqual(bE._TimeSeries, ts)

class BehavioralTimeSeriesConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        bts = BehavioralTimeSeries('test_bts', ts)
        self.assertEqual(bts.source, 'test_bts')
        self.assertEqual(bts._TimeSeries, ts)

class PupilTrackingConstructor(unittest.TestCase):
    def test_init(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        pt = BehavioralTimeSeries('test_pt', ts)
        self.assertEqual(pt.source, 'test_pt')
        self.assertEqual(pt._TimeSeries, ts)

class EyeTrackingConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        et = EyeTracking('test_et', sS)
        self.assertEqual(et.source, 'test_et')
        self.assertEqual(et._SpatialSeries, sS)

class CompassDirectionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        cd = CompassDirection('test_cd', sS)
        self.assertEqual(cd.source, 'test_cd')
        self.assertEqual(cd._SpatialSeries, sS)

class PositionConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        pc = Position('test_pc', sS)
        self.assertEqual(pc.source, 'test_pc')
        self.assertEqual(pc._SpatialSeries, sS)

class MotionCorrectionConstructor(unittest.TestCase):
    def test_init(self):
        mc = MotionCorrection('test_mc', list())
        self.assertEqual(mc.source, 'test_mc')

