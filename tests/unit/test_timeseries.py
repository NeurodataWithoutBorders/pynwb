import unittest

from pynwb import TimeSeries
from pynwb.core import NWBContainer

import numpy as np

class TimeSeriesConstructor(unittest.TestCase):

    def test_init_no_parent(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertIsNone(ts.parent)

    def test_init_datalink_set(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        self.assertSetEqual(ts.data_link, set())
        
    def test_init_timestampslink_set(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        self.assertSetEqual(ts.timestamps_link, set())

    def test_init_no_parent(self):
        parent = NWBContainer()
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list(), parent=parent)
        self.assertEqual(ts.name, 'test_ts')
        self.assertIs(ts.parent, parent)

    def test_init_data(self):
        dat = [0, 1, 2, 3, 4]
        tstamps = [0, 1, 2, 3, 4]
        ts = TimeSeries('test_ts', 'a hypothetical source', dat, 'Volts', timestamps=[0.1, 0.2, 0.3, 0.4])
        self.assertIs(ts.data, dat)
        self.assertEqual(ts.conversion, 1.0)
        self.assertIs(ts.resolution, np.nan)
        self.assertEqual(ts.unit, 'Volts')

    def test_init_timestamps(self):
        dat = [0, 1, 2, 3, 4]
        tstamps = [0.1, 0.2, 0.3, 0.4]
        ts = TimeSeries('test_ts', 'a hypothetical source', dat, 'unit', timestamps=tstamps)
        self.assertIs(ts.timestamps , tstamps)
        self.assertEqual(ts.interval, 1)
        self.assertEqual(ts.time_unit, "Seconds")

    def test_init_rate(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', starting_time=0.0, rate=1.0)
        self.assertEqual(ts.starting_time, 0.0)
        self.assertEqual(ts.rate, 1.0)
        self.assertEqual(ts.time_unit, "Seconds")

class TimeSeriesSetters(unittest.TestCase):

    def setUp(self):
        self.ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        
    def test_set_description(self):
        self.ts.set_description('this is a description')
        self.assertEqual(self.ts.description, 'this is a description')

    def test_set_comments(self):
        self.ts.set_comments('this is a comments')
        self.assertEqual(self.ts.comments, 'this is a comments')

