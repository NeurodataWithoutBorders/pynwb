import unittest2 as unittest
import numpy as np
from pynwb.base import TimeSeries
from pynwb.tools.tstools import TimeSeriesHelper


class TimeseriesTestCaseBase(unittest.TestCase):

    def test_subset_timeseries_numpy(self):
        ts_const_args = dict(name='test_ts',
                             source='a hypothetical source',
                             data=np.arange(200).reshape(100, 2),
                             unit='unit',
                             starting_time=3.0,
                             rate=1.0)
        subset_args = dict(name='subset_series', time_range=(4., 5.1))
        expected_data = [[2, 3], [4, 5]]
        expected_timestamps = [4.0, 5.0]

        # Construct the timeseries and subset
        ts_instance = TimeSeries(**ts_const_args)
        ts_helper_instance = TimeSeriesHelper(ts_instance)
        subset = ts_helper_instance.subset_series(**subset_args)

        # Assert the behavior
        self.assertListEqual(subset.data.tolist(), expected_data)
        self.assertListEqual(list(subset.get_timestamps()), expected_timestamps)

    def test_subset_timeseries_list(self):
        ts_const_args = dict(name='test_ts',
                             source='a hypothetical source',
                             data=np.arange(200).reshape(100, 2).tolist(),
                             unit='unit',
                             starting_time=3.0,
                             rate=1.0)
        subset_args = dict(name='subset_series', time_range=(4., 5.1))
        expected_data = [[2, 3], [4, 5]]
        expected_timestamps = [4.0, 5.0]

        # Construct the timeseries and subset
        ts_instance = TimeSeries(**ts_const_args)
        ts_helper_instance = TimeSeriesHelper(ts_instance)
        subset = ts_helper_instance.subset_series(**subset_args)

        # Assert the behavior
        self.assertListEqual(subset.data, expected_data)
        self.assertListEqual(list(subset.get_timestamps()), expected_timestamps)

    def test_time_to_index(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=list(range(10)),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        ts_helper = TimeSeriesHelper(ts)
        ri, rt = ts_helper.time_to_index(3.0)
        self.assertEqual(ri, 0)
        self.assertEqual(rt, 3.0)
        ri, rt = ts_helper.time_to_index(3.5, 'before')
        self.assertEqual(ri, 0)
        self.assertEqual(rt, 3.0)
        ri, rt = ts_helper.time_to_index(3.5, 'after')
        self.assertEqual(ri, 1)
        self.assertEqual(rt, 4.0)

    def test_time_to_index_no_match(self):
        ts = TimeSeries(name='test_ts',
                        source='a hypothetical source',
                        data=list(range(10)),
                        unit='unit',
                        starting_time=3.0,
                        rate=1.0)
        ts_helper = TimeSeriesHelper(ts)
        ri, rt = ts_helper.time_to_index(0.0)
        self.assertIsNone(ri)
        self.assertIsNone(rt)
        ri, rt = ts_helper.time_to_index(20.0)
        self.assertIsNone(ri)
        self.assertIsNone(rt)
