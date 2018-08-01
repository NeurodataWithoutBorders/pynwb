import unittest2 as unittest

from pynwb.base import ProcessingModule, TimeSeries
from pynwb.form.data_utils import DataChunkIterator
from pynwb.form.backends.hdf5 import H5DataIO


class TestProcessingModule(unittest.TestCase):

    def setUp(self):
        self.pm = ProcessingModule('test_procmod', 'PyNWB unit test, test_init', 'a fake processing module')

    def test_init(self):
        self.assertEqual(self.pm.name, 'test_procmod')
        self.assertEqual(self.pm.source, 'PyNWB unit test, test_init')
        self.assertEqual(self.pm.description, 'a fake processing module')

    def test_add_container(self):
        ts = TimeSeries('test_ts', 'unit test test_add_container', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_get_container(self):
        ts = TimeSeries('test_ts', 'unit test test_get_container', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        tmp = self.pm.get_container('test_ts')
        self.assertIs(tmp, ts)

    def test_getitem(self):
        ts = TimeSeries('test_ts', 'unit test test_getitem', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        tmp = self.pm['test_ts']
        self.assertIs(tmp, ts)


class TestTimeSeries(unittest.TestCase):

    def test_data_timeseries(self):
        ts1 = TimeSeries('test_ts1', 'unit test test_data_timeseries', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', 'unit test test_data_timeseries', ts1,
                         'grams', timestamps=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5])
        self.assertEqual(ts2.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts1.num_samples, ts2.num_samples)

    def test_timestamps_timeseries(self):
        ts1 = TimeSeries('test_ts1', 'unit test test_timestamps_timeseries', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', 'unit test test_data_timeseries', [10, 11, 12, 13, 14, 15],
                         'grams', timestamps=ts1)
        self.assertEqual(ts2.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def test_nodata(self):
        ts1 = TimeSeries('test_ts1', 'unit test test_DataIO', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, 0)

    def test_dataio_list_data(self):
        data = H5DataIO(list(range(100)))
        ts1 = TimeSeries('test_ts1', 'unit test test_DataIO', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, 100)

    def test_dataio_dci_data(self):
        data = H5DataIO(DataChunkIterator(data=(i for i in range(100))))
        ts1 = TimeSeries('test_ts1', 'unit test test_DataIO', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, -1)

    def test_dci_data(self):
        data = DataChunkIterator(data=(i for i in range(100)))
        ts1 = TimeSeries('test_ts1', 'unit test test_DataIO', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, -1)

    def test_no_time(self):
        with self.assertRaisesRegex(TypeError, "either 'timestamps' or 'rate' must be specified"):
            TimeSeries('test_ts2', 'unit test test_data_timeseries', [10, 11, 12, 13, 14, 15], 'grams')

    def test_no_starting_time(self):
        # if no starting_time is given, 0.0 is assumed
        ts1 = TimeSeries('test_ts1', 'unit test test_DataIO', rate=0.1)
        self.assertEqual(ts1.starting_time, 0.0)

    def test_conflicting_time_args(self):
        with self.assertRaises(ValueError):
            TimeSeries('test_ts2', 'unit test test_data_timeseries', [10, 11, 12, 13, 14, 15], 'grams', rate=30.,
                       timestamps=[.3, .4, .5, .6, .7, .8])
        with self.assertRaises(ValueError):
            TimeSeries('test_ts2', 'unit test test_data_timeseries', [10, 11, 12, 13, 14, 15], 'grams',
                       starting_time=30., timestamps=[.3, .4, .5, .6, .7, .8])
