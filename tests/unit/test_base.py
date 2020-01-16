import numpy as np

from pynwb.base import ProcessingModule, TimeSeries, Images, Image
from pynwb.testing import TestCase
from hdmf.data_utils import DataChunkIterator
from hdmf.backends.hdf5 import H5DataIO


class TestProcessingModule(TestCase):

    def setUp(self):
        self.pm = ProcessingModule('test_procmod', 'a fake processing module')

    def test_init(self):
        self.assertEqual(self.pm.name, 'test_procmod')
        self.assertEqual(self.pm.description, 'a fake processing module')

    def test_add_data_interface(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_deprecated_add_data_interface(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        with self.assertWarnsWith(PendingDeprecationWarning, 'add_data_interface will be replaced by add'):
            self.pm.add_data_interface(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_deprecated_add_container(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        with self.assertWarnsWith(PendingDeprecationWarning, 'add_container will be replaced by add'):
            self.pm.add_container(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_get_data_interface(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add(ts)
        tmp = self.pm.get('test_ts')
        self.assertIs(tmp, ts)
        self.assertIs(self.pm['test_ts'], self.pm.get('test_ts'))

    def test_deprecated_get_data_interface(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add(ts)
        with self.assertWarnsWith(PendingDeprecationWarning, 'get_data_interface will be replaced by get'):
            tmp = self.pm.get_data_interface('test_ts')
        self.assertIs(tmp, ts)

    def test_deprecated_get_container(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add(ts)
        with self.assertWarnsWith(PendingDeprecationWarning, 'get_container will be replaced by get'):
            tmp = self.pm.get_container('test_ts')
        self.assertIs(tmp, ts)

    def test_getitem(self):
        ts = TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                        'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.pm.add(ts)
        tmp = self.pm['test_ts']
        self.assertIs(tmp, ts)


class TestTimeSeries(TestCase):

    def test_init_no_parent(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())
        self.assertEqual(ts.name, 'test_ts')
        self.assertIsNone(ts.parent)

    def test_init_datalink_set(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())
        self.assertIsInstance(ts.data_link, set)
        self.assertEqual(len(ts.data_link), 0)

    def test_init_timestampslink_set(self):
        ts = TimeSeries('test_ts', list(), 'unit', timestamps=list())
        self.assertIsInstance(ts.timestamp_link, set)
        self.assertEqual(len(ts.timestamp_link), 0)

    def test_init_data(self):
        dat = [0, 1, 2, 3, 4]
        ts = TimeSeries('test_ts', dat, 'volts', timestamps=[0.1, 0.2, 0.3, 0.4])
        self.assertIs(ts.data, dat)
        self.assertEqual(ts.conversion, 1.0)
        self.assertEqual(ts.resolution, -1.0)
        self.assertEqual(ts.unit, 'volts')

    def test_init_timestamps(self):
        dat = [0, 1, 2, 3, 4]
        tstamps = [0.1, 0.2, 0.3, 0.4]
        ts = TimeSeries('test_ts', dat, 'unit', timestamps=tstamps)
        self.assertIs(ts.timestamps, tstamps)
        self.assertEqual(ts.interval, 1)
        self.assertEqual(ts.time_unit, "seconds")

    def test_init_rate(self):
        ts = TimeSeries('test_ts', list(), 'unit', starting_time=0.0, rate=1.0)
        self.assertEqual(ts.starting_time, 0.0)
        self.assertEqual(ts.rate, 1.0)
        self.assertEqual(ts.time_unit, "seconds")

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
        with self.assertWarns(UserWarning):
            self.assertIs(ts1.num_samples, None)

    def test_dataio_list_data(self):
        length = 100
        data = list(range(length))
        ts1 = TimeSeries('test_ts1', H5DataIO(data),
                         'grams', starting_time=0.0, rate=0.1)
        self.assertEqual(ts1.num_samples, length)
        assert data == list(ts1.data)

    def test_dataio_dci_data(self):

        def generator_factory():
            return (i for i in range(100))

        data = H5DataIO(DataChunkIterator(data=generator_factory()))
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        with self.assertWarnsWith(UserWarning, 'The data attribute on this TimeSeries (named: test_ts1) has a '
                                  '__len__, but it cannot be read'):
            self.assertIs(ts1.num_samples, None)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data(self):

        def generator_factory():
            return (i for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        with self.assertWarnsWith(UserWarning, 'The data attribute on this TimeSeries (named: test_ts1) has no '
                                  '__len__'):
            self.assertIs(ts1.num_samples, None)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data_arr(self):

        def generator_factory():
            return (np.array([i, i+1]) for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts1 = TimeSeries('test_ts1', data,
                         'grams', starting_time=0.0, rate=0.1)
        # with self.assertWarnsRegex(UserWarning, r'.*name: \'test_ts1\'.*'):
        with self.assertWarns(UserWarning):
            self.assertIs(ts1.num_samples, None)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_no_time(self):
        with self.assertRaisesWith(TypeError, "either 'timestamps' or 'rate' must be specified"):
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


class TestImage(TestCase):

    def test_image(self):
        Image(name='test_image', data=np.ones((10, 10)))


class TestImages(TestCase):

    def test_images(self):
        image = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        Images(name='images_name', images=[image, image2])
