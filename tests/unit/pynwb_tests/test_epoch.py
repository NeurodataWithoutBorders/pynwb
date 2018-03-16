import unittest

from pynwb.epoch import EpochTable, TimeSeriesIndex
from pynwb import TimeSeries
from pynwb.form.data_utils import ListSlicer

import numpy as np


class TimeSeriesIndexTest(unittest.TestCase):

    def test_init(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        tsi = TimeSeriesIndex()
        self.assertEqual(tsi.name, 'timeseries_index')
        tsi.add_row(40, 105, ts)
        self.assertEqual(tsi['count', 0], 105)
        self.assertEqual(tsi['idx_start', 0], 40)
        self.assertEqual(tsi['timeseries', 0], ts)


class EpochTableTest(unittest.TestCase):

    def test_init(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        tsi = TimeSeriesIndex()
        tsi.add_row(40, 105, ts)
        ept = EpochTable()
        self.assertEqual(ept.name, 'epochs')
        ept.add_row('a test epoch', 10.0, 20.0, "test,unittest,pynwb", ListSlicer(tsi.data, slice(0, 1)))
        row = ept[0]
        self.assertEqual(row[0], 'a test epoch')
        self.assertEqual(row[1], 10.0)
        self.assertEqual(row[2], 20.0)
        self.assertEqual(row[3], "test,unittest,pynwb")
        self.assertEqual(row[4].data, tsi.data)
        self.assertEqual(row[4].region, slice(0, 1))


class EpochSetters(unittest.TestCase):

    def setUp(self):
        # self.epoch = Epoch("test_epoch", 'a fake source', 10.0, 20.0, "this is an epoch")
        pass

    def test_add_tags(self):
        # self.epoch.add_tag("tag1")
        # self.epoch.add_tag("tag2")
        # self.assertListEqual(self.epoch.tags, ["tag1", "tag2"])
        pass

    def test_add_timeseries(self):
        # tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        # ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        # epoch_ts = self.epoch.add_timeseries(ts)
        # self.assertEqual(epoch_ts.count, 100)
        # self.assertEqual(epoch_ts.idx_start, 90)
        # self.assertIs(self.epoch.get_timeseries("test_ts"), epoch_ts)
        pass


if __name__ == '__main__':
    unittest.main()
