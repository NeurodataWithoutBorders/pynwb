import unittest

from pynwb.ui.timeseries import TimeSeries
from pynwb.ui.container import NWBContainer

import numpy as np

class TimeSeriesConstructor(unittest.TestCase):

    def test_init_no_parent(self):
        ts = TimeSeries('test_ts', 'a hypothetical source')
        self.assertEqual(ts.name, 'test_ts')
        self.assertIsNone(ts.parent)

    def test_init_datalink_set(self):
        ts = TimeSeries('test_ts', 'a hypothetical source')
        self.assertSetEqual(ts.data_link, set())
        
    def test_init_timestampslink_set(self):
        ts = TimeSeries('test_ts', 'a hypothetical source')
        self.assertSetEqual(ts.timestamps_link, set())

    def test_init_no_parent(self):
        parent = NWBContainer()
        ts = TimeSeries('test_ts', 'a hypothetical source', parent=parent)
        self.assertEqual(ts.name, 'test_ts')
        self.assertIs(ts.parent, parent)

    def test_init_data(self):
        ts = TimeSeries('test_ts', 'a hypothetical source',)
        self.assertIsNone(ts.data)

    def test_init_timestamps(self):
        ts = TimeSeries('test_ts', 'a hypothetical source',)
        self.assertIsNone(ts.timestamps)


class TimeSeriesSetters(unittest.TestCase):

    def setUp(self):
        self.ts = TimeSeries('test_ts', 'a hypothetical source',)

    def test_set_data(self):
        dat = [0, 1, 2, 3, 4]
        self.ts.set_data(dat, 'Volts')
        self.assertIs(self.ts.data, dat)
        self.assertEqual(self.ts.conversion, 1.0)
        self.assertIs(self.ts.resolution, np.nan)
        self.assertEqual(self.ts.unit, 'Volts')

    def test_set_timestamps(self):
        tstamps = [0, 1, 2, 3, 4]
        self.ts.set_time(tstamps, 'Volts')
        self.assertIs(self.ts.timestamps , tstamps)
        self.assertEqual(self.ts.interval, 1)
        self.assertEqual(self.ts.time_unit, "Seconds")
        
    def test_set_timestamps_by_rate(self):
        self.ts.set_time_by_rate(0.0, 1.0)
        self.assertEqual(self.ts.starting_time, 0.0)
        self.assertEqual(self.ts.rate, 1.0)
        self.assertEqual(self.ts.time_unit, "Seconds")

    def test_set_description(self):
        self.ts.set_description('this is a description')
        self.assertEqual(self.ts.description, 'this is a description')

    def test_set_comments(self):
        self.ts.set_comments('this is a comments')
        self.assertEqual(self.ts.comments, 'this is a comments')
