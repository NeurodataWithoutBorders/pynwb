import unittest

from pynwb.base import ProcessingModule, TimeSeries


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

    def test_timestamps_timeseries(self):
        ts1 = TimeSeries('test_ts1', 'unit test test_data_timeseries', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', 'unit test test_data_timeseries', [10, 11, 12, 13, 14, 15],
                         'grams', timestamps=ts1)
        self.assertEqual(ts2.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
