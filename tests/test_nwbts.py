

from pynwb.nwbts import TimeSeries
from pynwb.container import Container

import numpy as np

import unittest

class TimeSeriesConstructor(unittest.TestCase):

    def test_init_no_parent(self):
        ts = TimeSeries('test_ts')
        self.assertEqual(ts._name, 'test_ts')
        self.assertIsNone(ts._parent)

    def test_init_datalink_set(self):
        ts = TimeSeries('test_ts')
        self.assertSetEqual(ts.data_link, set())
        
    def test_init_timestampslink_set(self):
        ts = TimeSeries('test_ts')
        self.assertSetEqual(ts.timestamps_link, set())

    def test_init_no_parent(self):
        parent = Container()
        ts = TimeSeries('test_ts', parent)
        self.assertEqual(ts._name, 'test_ts')
        self.assertIs(ts._parent, parent)

    def test_init_data(self):
        ts = TimeSeries('test_ts')
        self.assertIsNone(ts._data)

    def test_init_timestamps(self):
        ts = TimeSeries('test_ts')
        self.assertIsNone(ts._timestamps)


class TimeSeriesSetters(unittest.TestCase):

    def setUp(self):
        self.ts = TimeSeries('test_ts')

    def test_set_data(self):
        dat = [0, 1, 2, 3, 4]
        self.ts.set_data(dat, 'Volts')
        self.assertIs(self.data, dat)
        self.assertEqual(self.conversion, 1.0)
        self.assertEqual(self.resolution, np.nan)
        self.assertEqual(self.unit, 'Volts')

    def test_set_timestamps(self):
        tstamps = [0, 1, 2, 3, 4]
        self.ts.set_timestamps(dat, 'Volts')
        self.assertIs(self.timestamps , tstamps)
        self.assertEqual(self.interval, 1)
        self.assertEqual(self.time_unit, "Seconds")
        
    def test_set_timestamps_by_rate(self):
        self.ts.set_time_by_rate(0.0, 1.0)
        self.starting_time(self.starting_time, 0.0)
        self.assertEqual(self.rate, 1.0)
        self.assertEqual(self.time_unit, "Seconds")

    def test_set_description(self):
        self.ts.set_description('this is a description')
        self.assertequal(self.ts.description, 'this is a description')

    def test_set_source(self):
        self.ts.set_source('this is a source')
        self.assertequal(self.ts.source, 'this is a source')

    def test_set_comments(self):
        self.ts.set_comments('this is a comments')
        self.assertequal(self.ts.comments, 'this is a comments')
