import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import tz

from pynwb.epoch import TimeIntervals
from pynwb import TimeSeries, NWBFile
from pynwb.base import TimeSeriesReference, TimeSeriesReferenceVectorData
from pynwb.testing import TestCase

from hdmf.backends.hdf5 import H5DataIO


class TimeIntervalsTest(TestCase):

    def test_init(self):
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float64)
        ts = TimeSeries(name="test_ts", data=list(range(len(tstamps))), unit='unit', timestamps=tstamps)
        ept = TimeIntervals(name='epochs', description="TimeIntervals unittest")
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
            TimeSeries(name='a', data=[1]*11, unit='unit', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', data=[1]*13, unit='unit', timestamps=np.linspace(0.1, 5, 13)),
        ]

    def get_dataframe(self):
        tsa, tsb = self.get_timeseries()
        return pd.DataFrame({
            'foo': [1, 2, 3, 4],
            'bar': ['fish', 'fowl', 'dog', 'cat'],
            'start_time': [0.2, 0.25, 0.30, 0.35],
            'stop_time': [0.25, 0.30, 0.40, 0.45],
            'timeseries': [[TimeSeriesReference(idx_start=0, count=11, timeseries=tsa)],
                           [TimeSeriesReference(idx_start=0, count=13, timeseries=tsb)],
                           [],
                           [TimeSeriesReference(idx_start=4, count=6, timeseries=tsb),
                            TimeSeriesReference(idx_start=3, count=4, timeseries=tsa)]],
            'keys': ['q', 'w', 'e', 'r'],
            'tags': [[], [], ['fizz', 'buzz'], ['qaz']]
        })

    def test_dataframe_roundtrip(self):
        df = self.get_dataframe()
        epochs = TimeIntervals.from_dataframe(df, name='test epochs')
        obtained = epochs.to_dataframe()

        self.assertTupleEqual(obtained.loc[3, 'timeseries'][1], df.loc[3, 'timeseries'][1])
        self.assertIsInstance(epochs.timeseries, TimeSeriesReferenceVectorData)
        self.assertIsInstance(obtained.loc[3, 'timeseries'][1], TimeSeriesReference)
        self.assertIsInstance(df.loc[3, 'timeseries'][1], TimeSeriesReference)
        self.assertEqual(obtained.loc[2, 'foo'], df.loc[2, 'foo'])

    def test_dataframe_roundtrip_drop_ts(self):
        df = self.get_dataframe()
        epochs = TimeIntervals.from_dataframe(df, name='test epochs')
        self.assertIsInstance(epochs.timeseries, TimeSeriesReferenceVectorData)
        obtained = epochs.to_dataframe(exclude=set(['timeseries', 'timeseries_index']))

        self.assertNotIn('timeseries', obtained.columns)
        self.assertEqual(obtained.loc[2, 'foo'], df.loc[2, 'foo'])

    def test_add_interval_basic(self):
        """Test adding interval with just start/stop times"""
        epochs = TimeIntervals(name='test_epochs')
        epochs.add_interval(start_time=10.0, stop_time=20.0)
        row = epochs[0]
        self.assertEqual(row.loc[0]['start_time'], 10.0)
        self.assertEqual(row.loc[0]['stop_time'], 20.0)

    def test_add_interval_tags_string(self):
        """Test adding interval with tags as comma-separated string"""
        epochs = TimeIntervals(name='test_epochs')
        epochs.add_interval(start_time=10.0, stop_time=20.0, tags='tag1, tag2, tag3')
        row = epochs[0]
        self.assertEqual(row.loc[0]['tags'], ['tag1', 'tag2', 'tag3'])

    def test_add_interval_tags_list(self):
        """Test adding interval with tags as list"""
        epochs = TimeIntervals(name='test_epochs')
        epochs.add_interval(start_time=10.0, stop_time=20.0, tags=['tag1', 'tag2', 'tag3'])
        row = epochs[0]
        self.assertEqual(row.loc[0]['tags'], ['tag1', 'tag2', 'tag3'])

    def test_add_interval_single_timeseries_timestamps(self):
        """Test adding interval with single TimeSeries using timestamps"""
        epochs = TimeIntervals(name='test_epochs')
        ts = TimeSeries(
            name='test_ts',
            data=list(range(100)),
            unit='units',
            timestamps=np.linspace(0, 10, 100)
        )
        epochs.add_interval(start_time=2.0, stop_time=4.0, timeseries=ts)
        row = epochs[0]
        self.assertEqual(len(row.loc[0]['timeseries']), 1)
        ts_ref = row.loc[0]['timeseries'][0]
        self.assertEqual(ts_ref.idx_start, 20)  # at t=2.0
        self.assertEqual(ts_ref.count, 20)      # from t=2.0 to t=4.0

    def test_add_interval_single_timeseries_timestamps_with_dataio(self):
        """Test adding interval with single TimeSeries using timestamps"""
        epochs = TimeIntervals(name='test_epochs')
        ts = TimeSeries(
            name='test_ts',
            data=list(range(100)),
            unit='units',
            timestamps=H5DataIO(np.linspace(0, 10, 100))
        )
        epochs.add_interval(start_time=2.0, stop_time=4.0, timeseries=ts)
        row = epochs[0]
        self.assertEqual(len(row.loc[0]['timeseries']), 1)
        ts_ref = row.loc[0]['timeseries'][0]
        self.assertEqual(ts_ref.idx_start, 20)  # at t=2.0
        self.assertEqual(ts_ref.count, 20)      # from t=2.0 to t=4.0

    def test_add_interval_single_timeseries_rate(self):
        """Test adding interval with single TimeSeries using starting_time and rate"""
        epochs = TimeIntervals(name='test_epochs')
        ts = TimeSeries(
            name='test_ts',
            data=list(range(100)),
            unit='units',
            starting_time=0.0,
            rate=10.0  # 10 samples per second
        )
        epochs.add_interval(start_time=2.0, stop_time=4.0, timeseries=ts)
        row = epochs[0]
        self.assertEqual(len(row.loc[0]['timeseries']), 1)
        ts_ref = row.loc[0]['timeseries'][0]
        self.assertEqual(ts_ref.idx_start, 20)  # at t=2.0
        self.assertEqual(ts_ref.count, 20)      # from t=2.0 to t=4.0

    def test_add_interval_multiple_timeseries(self):
        """Test adding interval with multiple TimeSeries"""
        epochs = TimeIntervals(name='test_epochs')
        ts1 = TimeSeries(
            name='test_ts1',
            data=list(range(100)),
            unit='units',
            timestamps=np.linspace(0, 10, 100)
        )
        ts2 = TimeSeries(
            name='test_ts2',
            data=list(range(50)),
            unit='units',
            starting_time=0.0,
            rate=5.0
        )
        epochs.add_interval(start_time=2.0, stop_time=4.0, timeseries=[ts1, ts2])
        row = epochs[0]
        self.assertEqual(len(row.loc[0]['timeseries']), 2)
        ts1_ref = row.loc[0]['timeseries'][0]
        ts2_ref = row.loc[0]['timeseries'][1]
        self.assertEqual(ts1_ref.idx_start, 20)
        self.assertEqual(ts1_ref.count, 20)
        self.assertEqual(ts2_ref.idx_start, 10)
        self.assertEqual(ts2_ref.count, 10)

    def test_add_interval_timeseries_missing_timing(self):
        """Test error when TimeSeries has neither timestamps nor starting_time/rate"""
        epochs = TimeIntervals(name='test_epochs')
        ts = TimeSeries(
            name='test_ts',
            data=list(range(100)),
            unit='units',
            timestamps=np.linspace(0, 10, 100)
        )
        ts.fields['timestamps'] = None  # remove timestamps to trigger error 
        msg = "TimeSeries object must have timestamps or starting_time and rate"
        with self.assertRaisesWith(ValueError, msg):
            epochs.add_interval(start_time=2.0, stop_time=4.0, timeseries=ts)

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

    def test_from_dataframe_missing_supplied_col(self):
        df = pd.DataFrame({'start_time': [1., 2., 3.], 'stop_time': [2., 3., 4.], 'label': ['a', 'b', 'c']})
        with self.assertRaises(ValueError):
            TimeIntervals.from_dataframe(df, name='ti_name', columns=[{'name': 'not there'}])
