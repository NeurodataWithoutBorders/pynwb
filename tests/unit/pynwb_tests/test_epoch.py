import unittest
from datetime import datetime
from dateutil import tz

from pynwb.epoch import TimeIntervals, TimeSeriesIndex
from pynwb import TimeSeries, NWBFile

import numpy as np
import pandas as pd


class TimeIntervalsTest(unittest.TestCase):

    def _get_time_intervals(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        ept = TimeIntervals('epochs', "TimeIntervals unittest")
        self.assertEqual(ept.name, 'epochs')
        ept.add_interval(10.0, 20.0, ["test", "unittest", "pynwb"], ts)
        return ept, (ts,)

    def test_init(self):
        ept, ts = self._get_time_intervals()
        row = ept[0]
        self.assertEqual(row[1], 10.0)
        self.assertEqual(row[2], 20.0)
        self.assertEqual(row[3], ["test", "unittest", "pynwb"])
        self.assertEqual(row[4], [(90, 100, ts[0])])

    def setUp(self):
        self.tsa, self.tsb = self.get_timeseries()
        self.columns = (
            [0.2, 0.25, 0.30, 0.35],
            [0.25, 0.30, 0.40, 0.45],
            [[], [], ['fizz', 'buzz'], ['qaz']],
            [[self.tsa], [self.tsb], [], [self.tsb, self.tsa]],
            ['q', 'w', 'e', 'r'],
            [1, 2, 3, 4],
            ['fish', 'fowl', 'dog', 'cat'],
        )
        self.colnames = (
                          'start_time',
                          'stop_time',
                          'tags',
                          'timeseries',
                          'description',
                          'foo',
                          'bar'
        )

    def get_timeseries(self):
        return [
            TimeSeries(name='a', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', timestamps=np.linspace(0.1, 5, 13)),
        ]

    def get_dataframe(self):
        return pd.DataFrame(dict(zip(self.colnames, self.columns)))

    def get_timeintervals(self):
        ept = TimeIntervals('epochs', "TimeIntervals unittest")
        for colname in self.colnames[4:]:
            ept.add_column(name=colname, description="test column: %s" % colname)
        for row in zip(*self.columns):
            kwargs = dict(zip(self.colnames, row))
            ept.add_interval(**kwargs)
        return ept

    def test_dataframe_roundtrip(self):
        df = self.get_dataframe()
        epochs = TimeIntervals.from_dataframe(df, name='test epochs')
        obtained = epochs.to_dataframe()

        self.assertIs(obtained.loc[3, 'timeseries'][1], df.loc[3, 'timeseries'][1])
        self.assertEqual(obtained.loc[2, 'foo'], df.loc[2, 'foo'])

    def test_no_tags(self):
        nwbfile = NWBFile("a file with header data", "NB123A", datetime(1970, 1, 1, tzinfo=tz.tzutc()))
        df = self.get_dataframe()
        for i, row in df.iterrows():
            nwbfile.add_epoch(start_time=row['start_time'], stop_time=row['stop_time'])

    def test_ts_index(self):
        ept = self.get_timeintervals()
        col = ept['timeseries']
        self.assertIsInstance(col.target, TimeSeriesIndex)


if __name__ == '__main__':
    unittest.main()
