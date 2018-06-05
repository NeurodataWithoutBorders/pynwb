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
        self.assertIsInstance(ts.data_link, set)
        self.assertEqual(len(ts.data_link), 0)

    def test_init_timestampslink_set(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list())
        self.assertIsInstance(ts.timestamp_link, set)
        self.assertEqual(len(ts.timestamp_link), 0)

    def test_init_no_parent(self):  # noqa: F811
        parent = NWBContainer('unit test: test_init_no_parent', 'test_parent_container')
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', timestamps=list(), parent=parent)
        self.assertEqual(ts.name, 'test_ts')
        self.assertIs(ts.parent, parent)

    def test_init_data(self):
        dat = [0, 1, 2, 3, 4]
        tstamps = [0, 1, 2, 3, 4]  # noqa: F841
        ts = TimeSeries('test_ts', 'a hypothetical source', dat, 'Volts', timestamps=[0.1, 0.2, 0.3, 0.4])
        self.assertIs(ts.data, dat)
        self.assertEqual(ts.conversion, 1.0)
        self.assertEqual(ts.resolution, 0.0)
        self.assertEqual(ts.unit, 'Volts')

    def test_init_timestamps(self):
        dat = [0, 1, 2, 3, 4]
        tstamps = [0.1, 0.2, 0.3, 0.4]
        ts = TimeSeries('test_ts', 'a hypothetical source', dat, 'unit', timestamps=tstamps)
        self.assertIs(ts.timestamps, tstamps)
        self.assertEqual(ts.interval, 1)
        self.assertEqual(ts.time_unit, "Seconds")

    def test_init_rate(self):
        ts = TimeSeries('test_ts', 'a hypothetical source', list(), 'unit', starting_time=0.0, rate=1.0)
        self.assertEqual(ts.starting_time, 0.0)
        self.assertEqual(ts.rate, 1.0)
        self.assertEqual(ts.time_unit, "Seconds")

    def test_time_to_index(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=list(range(10)),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        ri, rt = ts.time_to_index(3.0)
        self.assertEqual(ri, 0)
        self.assertEqual(rt, 3.0)
        ri, rt = ts.time_to_index(3.5, 'before')
        self.assertEqual(ri, 0)
        self.assertEqual(rt, 3.0)
        ri, rt = ts.time_to_index(3.5, 'after')
        self.assertEqual(ri, 1)
        self.assertEqual(rt, 4.0)

    def test_time_to_index_no_match(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=list(range(10)),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        ri, rt = ts.time_to_index(0.0)
        self.assertIsNone(ri)
        self.assertIsNone(rt)
        ri, rt = ts.time_to_index(20.0)
        self.assertIsNone(ri)
        self.assertIsNone(rt)

    def test_subset_timeseries_numpy(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=np.arange(200).reshape(100, 2),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        subset = ts.subset_series(name='subset_series', time_range=(4., 5.))
        self.assertListEqual(subset.data.tolist(), [[2, 3], [4, 5]])

    def test_subset_timeseries_list(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=np.arange(200).reshape(100, 2).tolist(),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        subset = ts.subset_series(name='subset_series', time_range=(4., 5.))
        self.assertListEqual(subset.data, [[2, 3], [4, 5]])
