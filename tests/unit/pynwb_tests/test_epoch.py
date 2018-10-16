import unittest

from pynwb.epoch import EpochTable
from pynwb import TimeSeries
from pynwb.form.data_utils import ListSlicer

import numpy as np
import pandas as pd


#class TimeSeriesIndexTest(unittest.TestCase):
#
#    def test_init(self):
#        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
#        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
#        tsi = TimeSeriesIndex()
#        self.assertEqual(tsi.name, 'timeseries_index')
#        tsi.add_row(40, 105, ts)
#        self.assertEqual(tsi['count', 0], 105)
#        self.assertEqual(tsi['idx_start', 0], 40)
#        self.assertEqual(tsi['timeseries', 0], ts)
#

class EpochTableTest(unittest.TestCase):

    def test_init(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        ept = EpochTable("EpochTable unittest")
        self.assertEqual(ept.name, 'epochs')
        ept.add_epoch(10.0, 20.0, ["test", "unittest", "pynwb"], ts)
        row = ept[0]
        self.assertEqual(row[1], 10.0)
        self.assertEqual(row[2], 20.0)
        self.assertEqual(row[3], ["test", "unittest", "pynwb"])
        self.assertEqual(row[4], [(90, 100, ts)])


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


class TestEpochsDf(unittest.TestCase):

    def get_timeseries(self):
        return [
            TimeSeries(name='a', source='test', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', source='test', timestamps=np.linspace(0.1, 5, 13)),
        ]

    def get_dataframe(self):
        tsa, tsb = self.get_timeseries()
        return pd.DataFrame({
            'foo': [1, 2, 3, 4],
            'bar': ['fish', 'fowl', 'dog', 'cat'],
            'start_time': [0.2, 0.25, 0.30, 0.35],
            'end': [0.25, 0.30, 0.40, 0.45],
            'timeseries': [[tsa], [tsb], [], [tsb, tsa]],
            'description': ['q', 'w', 'e', 'r'],
            'tags': [[], [], ['fizz', 'buzz'], ['qaz']]
        })

    def test_dataframe_roundtrip(self):
        df = self.get_dataframe()
        epochs = EpochTable.from_dataframe(df, name='test epochs', source='testing', stop_times='end')
        obtained = epochs.to_dataframe()

        assert set(df.columns) ^ set(obtained.columns) == set(['stop_time', 'end'])
        assert obtained.loc[3, 'timeseries'][1] is df.loc[3, 'timeseries'][1]
        assert obtained.loc[2, 'foo'] == df.loc[2, 'foo']


if __name__ == '__main__':
    unittest.main()
