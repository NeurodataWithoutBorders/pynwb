import numpy as np

from pynwb.base import ProcessingModule, TimeSeries, Images, Image, TimeSeriesReferenceVectorData, TimeSeriesReference
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

    def test_good_continuity_timeseries(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                         continuity='continuous')
        self.assertEqual(ts1.continuity, 'continuous')

    def test_bad_continuity_timeseries(self):
        with self.assertRaises(ValueError):
            TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                       'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                       continuity='wrong')

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
        ts1 = TimeSeries('test_ts1', data=[1, 2, 3], unit='unit', rate=0.1)
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


class TestTimeSeriesReferenceVectorData(TestCase):

    def test_init(self):
        temp = TimeSeriesReferenceVectorData()
        self.assertEqual(temp.name, 'timeseries')
        self.assertEqual(temp.description,
                         "Column storing references to a TimeSeries (rows). For each TimeSeries this "
                         "VectorData column stores the start_index and count to indicate the range in time "
                         "to be selected as well as an object reference to the TimeSeries.")
        self.assertListEqual(temp.data, [])
        temp = TimeSeriesReferenceVectorData(name='test', description='test')
        self.assertEqual(temp.name, 'test')
        self.assertEqual(temp.description, 'test')

    def test_get_empty(self):
        """Get data from an empty TimeSeriesReferenceVectorData"""
        temp = TimeSeriesReferenceVectorData()
        self.assertListEqual(temp[:], [])
        with self.assertRaises(IndexError):
            temp[0]

    def test_get_length1_valid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with one element and valid data"""
        temp = TimeSeriesReferenceVectorData()
        value = TimeSeriesReference(0, 5, TimeSeries(name='test', description='test',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        temp.append(value)
        self.assertTupleEqual(temp[0], value)
        self.assertListEqual(temp[:], [TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*value), ])

    def test_get_length1_invalid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with one element and invalid data"""
        temp = TimeSeriesReferenceVectorData()
        value = TimeSeriesReference(-1, -1, TimeSeries(name='test', description='test',
                                                       data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        temp.append(value)
        # test index slicing
        re = temp[0]
        self.assertTrue(isinstance(re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
        self.assertTupleEqual(re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE)
        # test array slicing and list slicing
        selection = [slice(None), [0, ]]
        for s in selection:
            re = temp[s]
            self.assertTrue(isinstance(re, list))
            self.assertTrue(len(re), 1)
            self.assertTrue(isinstance(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
            self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE)

    def test_get_length5_valid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with 5 elements"""
        temp = TimeSeriesReferenceVectorData()
        num_values = 5
        values = [TimeSeriesReference(0, 5, TimeSeries(name='test'+str(i), description='test',
                                                       data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
                  for i in range(num_values)]
        for v in values:
            temp.append(v)
        # Test single element selection
        for i in range(num_values):
            # test index slicing
            re = temp[i]
            self.assertTupleEqual(re, values[i])
            # test slicing
            re = temp[i:i+1]
            self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[i]))
        # Test multi element selection
        re = temp[0:2]
        self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[0]))
        self.assertTupleEqual(re[1], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[1]))

    def test_get_length5_with_invalid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with 5 elements"""
        temp = TimeSeriesReferenceVectorData()
        num_values = 5
        values = [TimeSeriesReference(0, 5, TimeSeries(name='test'+str(i+1), description='test',
                                                       data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
                  for i in range(num_values-2)]
        values = ([TimeSeriesReference(-1, -1, TimeSeries(name='test'+str(0), description='test',
                                                          data=np.arange(10), unit='unit', starting_time=5.0,
                                                          rate=0.1)), ]
                  + values
                  + [TimeSeriesReference(-1, -1, TimeSeries(name='test'+str(5), description='test',
                                         data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1)), ])
        for v in values:
            temp.append(v)
        # Test single element selection
        for i in range(num_values):
            # test index slicing
            re = temp[i]
            if i in [0, 4]:
                self.assertTrue(isinstance(re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
                self.assertTupleEqual(re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE)
            else:
                self.assertTupleEqual(re, values[i])
            # test slicing
            re = temp[i:i+1]
            if i in [0, 4]:
                self.assertTrue(isinstance(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE))
                self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE)
            else:
                self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[i]))
        # Test multi element selection
        re = temp[0:2]
        self.assertTupleEqual(re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE)
        self.assertTupleEqual(re[1], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[1]))

    def test_add_row_restricted_type(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        with self.assertRaisesWith(TypeError, "TimeSeriesReferenceVectorData.add_row: incorrect type for "
                                              "'val' (got 'int', expected 'TimeSeriesReference')"):
            v.add_row(1)

    def test_append_restricted_type(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        with self.assertRaisesWith(TypeError, "TimeSeriesReferenceVectorData.append: incorrect type for "
                                              "'arg' (got 'float', expected 'TimeSeriesReference')"):
            v.append(2.0)


class TestTimeSeriesReference(TestCase):

    def test_check_types(self):
        # invalid selection but with correct types
        tsr = TimeSeriesReference(-1, -1, TimeSeries(name='test'+str(0), description='test',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        self.assertTrue(tsr.check_types())
        # invalid types, use float instead of int for both idx_start and count
        tsr = TimeSeriesReference(1.0, 5.0, TimeSeries(name='test'+str(0), description='test',
                                                       data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(TypeError, "idx_start must be an integer not <class 'float'>"):
            tsr.check_types()
        # invalid types, use float instead of int for idx_start only
        tsr = TimeSeriesReference(1.0, 5, TimeSeries(name='test'+str(0), description='test',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(TypeError, "idx_start must be an integer not <class 'float'>"):
            tsr.check_types()
        # invalid types, use float instead of int for count only
        tsr = TimeSeriesReference(1, 5.0, TimeSeries(name='test'+str(0), description='test',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(TypeError, "count must be an integer <class 'float'>"):
            tsr.check_types()
        # invalid type for TimeSeries but valid idx_start and count
        tsr = TimeSeriesReference(1, 5, None)
        with self.assertRaisesWith(TypeError, "timeseries must be of type TimeSeries. <class 'NoneType'>"):
            tsr.check_types()

    def test_is_invalid(self):
        tsr = TimeSeriesReference(-1, -1, TimeSeries(name='test'+str(0), description='test',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        self.assertFalse(tsr.isvalid())

    def test_is_valid(self):
        tsr = TimeSeriesReference(0, 10, TimeSeries(name='test'+str(0), description='test',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        self.assertTrue(tsr.isvalid())

    def test_is_valid_bad_index(self):
        # Error: negative start_index but positive count
        tsr = TimeSeriesReference(-1, 10, TimeSeries(name='test0', description='test0',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'idx_start' -1 out of range for timeseries 'test0'"):
            tsr.isvalid()
        # Error: start_index too large
        tsr = TimeSeriesReference(10, 0, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'idx_start' 10 out of range for timeseries 'test0'"):
            tsr.isvalid()
        # Error: positive start_index but negative count
        tsr = TimeSeriesReference(0, -3, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'count' -3 invalid. 'count' must be positive"):
            tsr.isvalid()
        # Error:  start_index + count too large
        tsr = TimeSeriesReference(3, 10, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'idx_start + count' out of range for timeseries 'test0'"):
            tsr.isvalid()

    def test_timestamps_property(self):
        # Timestamps from starting_time and rate
        tsr = TimeSeriesReference(5, 4, TimeSeries(name='test0', description='test0',
                                                   data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        np.testing.assert_array_equal(tsr.timestamps, np.array([5.5, 5.6, 5.7, 5.8]))
        # Timestamps from timestamps directly
        tsr = TimeSeriesReference(5, 4, TimeSeries(name='test0', description='test0',
                                                   data=np.arange(10), unit='unit',
                                                   timestamps=np.arange(10).astype(float)))
        np.testing.assert_array_equal(tsr.timestamps, np.array([5., 6., 7., 8.]))

    def test_timestamps_property_invalid_reference(self):
        # Timestamps from starting_time and rate
        tsr = TimeSeriesReference(-1, -1, TimeSeries(name='test0', description='test0',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        self.assertIsNone(tsr.timestamps)

    def test_timestamps_property_bad_reference(self):
        tsr = TimeSeriesReference(0, 12, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit',
                                                    timestamps=np.arange(10).astype(float)))
        with self.assertRaisesWith(IndexError, "'idx_start + count' out of range for timeseries 'test0'"):
            tsr.timestamps
        tsr = TimeSeriesReference(0, 12, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'idx_start + count' out of range for timeseries 'test0'"):
            tsr.timestamps

    def test_data_property(self):
        tsr = TimeSeriesReference(5, 4, TimeSeries(name='test0', description='test0',
                                                   data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        np.testing.assert_array_equal(tsr.data, np.array([5., 6., 7., 8.]))

    def test_data_property_invalid_reference(self):
        tsr = TimeSeriesReference(-1, -1, TimeSeries(name='test0', description='test0',
                                                     data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        self.assertIsNone(tsr.data)

    def test_data_property_bad_reference(self):
        tsr = TimeSeriesReference(0, 12, TimeSeries(name='test0', description='test0',
                                                    data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(IndexError, "'idx_start + count' out of range for timeseries 'test0'"):
            tsr.data
