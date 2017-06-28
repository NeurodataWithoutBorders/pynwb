import unittest

from pynwb.epoch import Epoch, EpochTimeSeries
from pynwb import TimeSeries

import numpy as np

class EpochTimeSeriesConstructor(unittest.TestCase):

    def test_init_timestamps(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        epoch_ts = EpochTimeSeries(ts, 5.0, 15.5)
        self.assertEqual(epoch_ts.count, 105)
        self.assertEqual(epoch_ts.idx_start, 40)

    def test_init_sample_rate(self):
        #self.ts.set_time_by_rate(1.0, 10.0)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(200)), 'unit', starting_time=1.0, rate=10.0)
        epoch_ts = EpochTimeSeries(ts, 5.0, 15.5)
        self.assertEqual(epoch_ts.count, 105)
        self.assertEqual(epoch_ts.idx_start, 40)

class EpochConstructor(unittest.TestCase):

    def test_init(self):
        epoch = Epoch("test_epoch", 100.0, 200.0, "this is an epoch")
        self.assertEqual(epoch.name, "test_epoch")
        self.assertEqual(epoch.start_time, 100.0)
        self.assertEqual(epoch.stop_time, 200.0)
        self.assertEqual(epoch.description, "this is an epoch")

class EpochSetters(unittest.TestCase):

    def setUp(self):
        self.epoch = Epoch("test_epoch", 10.0, 20.0, "this is an epoch")

    def test_add_tags(self):
        self.epoch.add_tag("tag1")
        self.epoch.add_tag("tag2")
        self.assertListEqual(self.epoch.tags, ["tag1", "tag2"])

    def test_add_timeseries(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        epoch_ts = self.epoch.add_timeseries(ts)
        self.assertEqual(epoch_ts.count, 100)
        self.assertEqual(epoch_ts.idx_start, 90)
        self.assertIs(self.epoch.get_timeseries("test_ts"), epoch_ts)


if __name__ == '__main__':
    unittest.main()
