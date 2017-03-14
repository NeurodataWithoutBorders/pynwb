import unittest

from pynwb import TimeSeries
from pynwb.behavior import SpatialSeries, BehavioralEpochs, BehavioralEvents, BehavioralTimeSeries, PupilTracking, EyeTracking, CompassDirection, Position, MotionCorrection

import numpy as np


class SpatialSeriesConstructor(unittest.TestCase):
    def test_init(self):
        sS = SpatialSeries('test_sS', 'a hypothetical source', list(), 'reference_frame', timestamps=list())
        self.assertEqual(sS.name, 'test_sS')
        self.assertEqual(sS.source, 'a hypothetical source')
        self.assertEqual(sS.unit, 'meters')
        self.assertEqual(sS.reference_frame, 'reference_frame')


class Constructor(unittest.TestCase):
    def test_init(self):
        pass

class BehavioralEpochsConstructor(unittest.TestCase):
    def test_init(self):
        pass

class BehavioralEventsConstructor(unittest.TestCase):
    def test_init(self):
        pass

class BehavioralTimeSeriesConstructor(unittest.TestCase):
    def test_init(self):
        pass

class PupilTrackingConstructor(unittest.TestCase):
    def test_init(self):
        pass

class EyeTrackingConstructor(unittest.TestCase):
    def test_init(self):
        pass

class CompassDirectionConstructor(unittest.TestCase):
    def test_init(self):
        pass

class PositionConstructor(unittest.TestCase):
    def test_init(self):
        pass

class MotionCorrectionConstructor(unittest.TestCase):
    def test_init(self):
        pass

