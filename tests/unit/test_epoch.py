import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import tz

from pynwb.epoch import TimeIntervals
from pynwb import TimeSeries, NWBFile
from pynwb.testing import TestCase


class TimeIntervalsTest(TestCase):

    def test_init(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        ept = TimeIntervals('epochs', "TimeIntervals unittest")
        self.assertEqual(ept.name, 'epochs')
        ept.add_interval(10.0, 20.0, ["test", "unittest", "pynwb"], ts)
        row = ept[0]
        self.assertEqual(row.index[0], 0)
        self.assertEqual(row.loc[0]['start_time'], 10.0)
        self.assertEqual(row.loc[0]['stop_time'], 20.0)
        self.assertEqual(row.loc[0]['tags'], ["test", "unittest", "pynwb"])
        self.assertEqual(row.loc[0]['timeseries'], [(90, 100, ts)])

    def get_timeseries(self):
        return [
            TimeSeries(name='a', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', timestamps=np.linspace(0.1, 5, 13)),
        ]

    def get_dataframe(self):
        tsa, tsb = self.get_timeseries()
        return pd.DataFrame({
            'foo': [1, 2, 3, 4],
            'bar': ['fish', 'fowl', 'dog', 'cat'],
            'start_time': [0.2, 0.25, 0.30, 0.35],
            'stop_time': [0.25, 0.30, 0.40, 0.45],
            'timeseries': [[tsa], [tsb], [], [tsb, tsa]],
            'keys': ['q', 'w', 'e', 'r'],
            'tags': [[], [], ['fizz', 'buzz'], ['qaz']]
        })

    def test_dataframe_roundtrip(self):
        df = self.get_dataframe()
        epochs = TimeIntervals.from_dataframe(df, name='test epochs')
        obtained = epochs.to_dataframe()

        self.assertIs(obtained.loc[3, 'timeseries'][1], df.loc[3, 'timeseries'][1])
        self.assertEqual(obtained.loc[2, 'foo'], df.loc[2, 'foo'])

    def test_dataframe_roundtrip_drop_ts(self):
        df = self.get_dataframe()
        epochs = TimeIntervals.from_dataframe(df, name='test epochs')
        obtained = epochs.to_dataframe(exclude=set(['timeseries', 'timeseries_index']))

        self.assertNotIn('timeseries', obtained.columns)
        self.assertEqual(obtained.loc[2, 'foo'], df.loc[2, 'foo'])

    def test_no_tags(self):
        nwbfile = NWBFile("a file with header data", "NB123A", datetime(1970, 1, 1, tzinfo=tz.tzutc()))
        df = self.get_dataframe()
        for i, row in df.iterrows():
            nwbfile.add_epoch(start_time=row['start_time'], stop_time=row['stop_time'])

    def test_from_dataframe(self):
        df = pd.DataFrame({'start_time': [1., 2., 3.], 'stop_time': [2., 3., 4.], 'label': ['a', 'b', 'c']},
                          columns=('start_time', 'stop_time', 'label'))
        ti = TimeIntervals.from_dataframe(df, name='ti_name')

        self.assertEqual(ti.colnames, ('start_time', 'stop_time', 'label'))
        self.assertEqual(ti.columns[0].data, [1.0, 2.0, 3.0])
        self.assertEqual(ti.columns[2].data, ['a', 'b', 'c'])

    def test_from_dataframe_missing_required_cols(self):
        df = pd.DataFrame({'start_time': [1., 2., 3.], 'label': ['a', 'b', 'c']})
        with self.assertRaises(ValueError):
            TimeIntervals.from_dataframe(df, name='ti_name')

    def test_frorm_dataframe_missing_supplied_col(self):
        df = pd.DataFrame({'start_time': [1., 2., 3.], 'stop_time': [2., 3., 4.], 'label': ['a', 'b', 'c']})
        with self.assertRaises(ValueError):
            TimeIntervals.from_dataframe(df, name='ti_name', columns=[{'name': 'not there'}])
