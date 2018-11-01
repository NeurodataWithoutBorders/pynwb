import unittest2 as unittest
import numpy as np

from pynwb.base import ProcessingModule, TimeSeries, Images, Image
from pynwb.form.data_utils import DataChunkIterator
from pynwb.form.backends.hdf5 import H5DataIO


class TestProcessingModule(unittest.TestCase):

    def setUp(self):
        self.pm = ProcessingModule('test_procmod', 'a fake processing module')

    def test_init(self):
        self.assertEqual(self.pm.name, 'test_procmod')
        self.assertEqual(self.pm.description, 'a fake processing module')

    def test_add_container(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_get_container(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        tmp = self.pm.get_container('test_ts')
        self.assertIs(tmp, ts)

    def test_getitem(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add_container(ts)
        tmp = self.pm['test_ts']
        self.assertIs(tmp, ts)


class TestTimeSeries(unittest.TestCase):

    def test_data_timeseries(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', ts1, 'grams', timestamps=[1.0, 1.1, 1.2,
                         1.3, 1.4, 1.5])
        self.assertEqual(ts2.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ts1.num_samples, ts2.num_samples)

    def test_timestamps_timeseries(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', [10, 11, 12, 13, 14, 15],
                         'grams', timestamps=ts1)
        self.assertEqual(ts2.timestamps, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def test_nodata(self):
        ts1 = TimeSeries('test_ts1', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, 0)

    def test_dataio_list_data(self):
        num_samples = 100
        data = list(range(num_samples))
        ts1 = TimeSeries('test_ts1', H5DataIO(data),
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, num_samples)
        assert data == list(ts1.data)

    def test_dataio_dci_data(self):

        def generator_factory():
            return (i for i in range(100))

        data = H5DataIO(DataChunkIterator(data=generator_factory()))
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, -1)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data(self):

        def generator_factory():
            return (i for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, -1)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data_arr(self):

        def generator_factory():
            return (np.array([i, i+1]) for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, -1)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_no_time(self):
        with self.assertRaisesRegex(TypeError, "either 'timestamps' or 'rate' must be specified"):
            TimeSeries('test_ts2', [10, 11, 12, 13, 14, 15], 'grams')

    def test_no_starting_time(self):
        # if no starting_time is given, 0.0 is assumed
        ts1 = TimeSeries('test_ts1', rate=0.1)
        self.assertEqual(ts1.starting_time, 0.0)

    def test_conflicting_time_args(self):
        with self.assertRaises(ValueError):
            TimeSeries('test_ts2', [10, 11, 12, 13, 14, 15], 'grams', rate=30.,
                       timestamps=[.3, .4, .5, .6, .7, .8])
        with self.assertRaises(ValueError):
            TimeSeries('test_ts2', [10, 11, 12, 13, 14, 15], 'grams',
                       starting_time=30., timestamps=[.3, .4, .5, .6, .7, .8])


class TestImage(unittest.TestCase):

    def test_image(self):
        Image(name='test_image', data=np.ones((10, 10)))


class TestImages(unittest.TestCase):

    def test_images(self):
        image = Image(name='test_image', data=np.ones((10, 10)))
        Images(name='images_name', images=[image, image])
