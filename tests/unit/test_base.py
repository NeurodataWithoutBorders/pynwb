import numpy as np
from numpy.testing import assert_array_equal

from pynwb.base import (
    ProcessingModule,
    TimeSeries,
    Images,
    Image,
    TimeSeriesReferenceVectorData,
    TimeSeriesReference,
    ImageReferences
)
from pynwb.testing import TestCase
from pynwb.testing.mock.base import mock_TimeSeries
from hdmf.data_utils import DataChunkIterator
from hdmf.backends.hdf5 import H5DataIO


class TestProcessingModule(TestCase):
    def setUp(self):
        self.pm = ProcessingModule(
            name="test_procmod", description="a test processing module"
        )

    def _create_time_series(self):
        ts = TimeSeries(
            name="test_ts",
            data=[0, 1, 2, 3, 4, 5],
            unit="grams",
            timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        )
        return ts

    def test_init(self):
        """Test creating a ProcessingModule."""
        self.assertEqual(self.pm.name, "test_procmod")
        self.assertEqual(self.pm.description, "a test processing module")

    def test_add_data_interface(self):
        """Test adding a data interface to a ProcessingModule using add(...) and retrieving it."""
        ts = self._create_time_series()
        self.pm.add(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_deprecated_add_data_interface(self):
        ts = self._create_time_series()
        with self.assertWarnsWith(
            PendingDeprecationWarning, "add_data_interface will be replaced by add"
        ):
            self.pm.add_data_interface(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_deprecated_add_container(self):
        ts = self._create_time_series()
        with self.assertWarnsWith(
            PendingDeprecationWarning, "add_container will be replaced by add"
        ):
            self.pm.add_container(ts)
        self.assertIn(ts.name, self.pm.containers)
        self.assertIs(ts, self.pm.containers[ts.name])

    def test_get_data_interface(self):
        """Test adding a data interface to a ProcessingModule and retrieving it using get(...)."""
        ts = self._create_time_series()
        self.pm.add(ts)
        tmp = self.pm.get("test_ts")
        self.assertIs(tmp, ts)
        self.assertIs(self.pm["test_ts"], self.pm.get("test_ts"))

    def test_deprecated_get_data_interface(self):
        ts = self._create_time_series()
        self.pm.add(ts)
        with self.assertWarnsWith(
            PendingDeprecationWarning, "get_data_interface will be replaced by get"
        ):
            tmp = self.pm.get_data_interface("test_ts")
        self.assertIs(tmp, ts)

    def test_deprecated_get_container(self):
        ts = self._create_time_series()
        self.pm.add(ts)
        with self.assertWarnsWith(
            PendingDeprecationWarning, "get_container will be replaced by get"
        ):
            tmp = self.pm.get_container("test_ts")
        self.assertIs(tmp, ts)

    def test_getitem(self):
        """Test adding a data interface to a ProcessingModule and retrieving it using __getitem__(...)."""
        ts = self._create_time_series()
        self.pm.add(ts)
        tmp = self.pm["test_ts"]
        self.assertIs(tmp, ts)


class TestTimeSeries(TestCase):
    def test_init_no_parent(self):
        """Test creating an empty TimeSeries and that it has no parent."""
        ts = TimeSeries(name="test_ts", data=list(), unit="unit", timestamps=list())
        self.assertEqual(ts.name, "test_ts")
        self.assertIsNone(ts.parent)

    def test_init_datalink_set(self):
        """Test creating a TimeSeries and that data_link is an empty set."""
        ts = TimeSeries(name="test_ts", data=list(), unit="unit", timestamps=list())
        self.assertIsInstance(ts.data_link, set)
        self.assertEqual(len(ts.data_link), 0)

    def test_init_timestampslink_set(self):
        """Test creating a TimeSeries and that timestamps_link is an empty set."""
        ts = TimeSeries(name="test_ts", data=list(), unit="unit", timestamps=list())
        self.assertIsInstance(ts.timestamp_link, set)
        self.assertEqual(len(ts.timestamp_link), 0)

    def test_init_data_timestamps(self):
        data = [0, 1, 2, 3, 4]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4]
        ts = TimeSeries(name="test_ts", data=data, unit="volts", timestamps=timestamps)
        self.assertIs(ts.data, data)
        self.assertIs(ts.timestamps, timestamps)
        self.assertEqual(ts.conversion, 1.0)
        self.assertEqual(ts.offset, 0.0)
        self.assertEqual(ts.resolution, -1.0)
        self.assertEqual(ts.unit, "volts")
        self.assertEqual(ts.interval, 1)
        self.assertEqual(ts.time_unit, "seconds")
        self.assertEqual(ts.num_samples, 5)
        self.assertIsNone(ts.continuity)
        self.assertIsNone(ts.rate)
        self.assertIsNone(ts.starting_time)

    def test_init_conversion_offset(self):
        data = [0, 1, 2, 3, 4]
        timestamps = [0.0, 0.1, 0.2, 0.3, 0.4]
        conversion = 2.1
        offset = 1.2
        ts = TimeSeries(
            name="test_ts",
            data=data,
            unit="volts",
            timestamps=timestamps,
            conversion=conversion,
            offset=offset,
        )
        self.assertIs(ts.data, data)
        self.assertEqual(ts.conversion, conversion)
        self.assertEqual(ts.offset, offset)

    def test_no_time(self):
        with self.assertRaisesWith(
            TypeError, "either 'timestamps' or 'rate' must be specified"
        ):
            TimeSeries(name="test_ts2", data=[10, 11, 12, 13, 14, 15], unit="grams")

    def test_no_starting_time(self):
        """Test that if no starting_time is given, 0.0 is assumed."""
        ts1 = TimeSeries(name="test_ts1", data=[1, 2, 3], unit="unit", rate=0.1)
        self.assertEqual(ts1.starting_time, 0.0)

    def test_init_rate(self):
        ts = TimeSeries(
            name="test_ts",
            data=list(),
            unit="volts",
            starting_time=1.0,
            rate=2.0,
        )
        self.assertEqual(ts.starting_time, 1.0)
        self.assertEqual(ts.starting_time_unit, "seconds")
        self.assertEqual(ts.rate, 2.0)
        self.assertEqual(ts.time_unit, "seconds")
        self.assertIsNone(ts.timestamps)

    def test_data_timeseries(self):
        """Test that setting a TimeSeries.data to another TimeSeries links the data correctly."""
        data = [0, 1, 2, 3]
        timestamps1 = [0.0, 0.1, 0.2, 0.3]
        timestamps2 = [1.0, 1.1, 1.2, 1.3]
        ts1 = TimeSeries(
            name="test_ts1", data=data, unit="grams", timestamps=timestamps1
        )
        ts2 = TimeSeries(
            name="test_ts2", data=ts1, unit="grams", timestamps=timestamps2
        )
        self.assertEqual(ts2.data, data)
        self.assertEqual(ts1.num_samples, ts2.num_samples)
        self.assertEqual(ts1.data_link, set([ts2]))

    def test_timestamps_timeseries(self):
        """Test that setting a TimeSeries.timestamps to another TimeSeries links the timestamps correctly."""
        data1 = [0, 1, 2, 3]
        data2 = [10, 11, 12, 13]
        timestamps = [0.0, 0.1, 0.2, 0.3]
        ts1 = TimeSeries(
            name="test_ts1", data=data1, unit="grams", timestamps=timestamps
        )
        ts2 = TimeSeries(name="test_ts2", data=data2, unit="grams", timestamps=ts1)
        self.assertEqual(ts2.timestamps, timestamps)
        self.assertEqual(ts1.timestamp_link, set([ts2]))

    def test_good_continuity_timeseries(self):
        ts = TimeSeries(
            name="test_ts1",
            data=[0, 1, 2, 3, 4, 5],
            unit="grams",
            timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            continuity="continuous",
        )
        self.assertEqual(ts.continuity, "continuous")

    def test_bad_continuity_timeseries(self):
        msg = (
            "TimeSeries.__init__: forbidden value for 'continuity' (got 'wrong', "
            "expected ['continuous', 'instantaneous', 'step'])"
        )
        with self.assertRaisesWith(ValueError, msg):
            TimeSeries(
                name="test_ts1",
                data=[0, 1, 2, 3, 4, 5],
                unit="grams",
                timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                continuity="wrong",
            )

    def _create_time_series_with_data(self, data):
        ts = TimeSeries(name="test_ts1", data=data, unit="grams", rate=0.1)
        return ts

    def test_dataio_list_data(self):
        length = 100
        data = list(range(length))
        ts = self._create_time_series_with_data(data)
        self.assertEqual(ts.num_samples, length)
        assert data == list(ts.data)

    def test_dataio_dci_data(self):
        def generator_factory():
            return (i for i in range(100))

        data = H5DataIO(DataChunkIterator(data=generator_factory()))
        ts = self._create_time_series_with_data(data)
        with self.assertWarnsWith(
            UserWarning,
            "The data attribute on this TimeSeries (named: test_ts1) has a "
            "__len__, but it cannot be read",
        ):
            self.assertIsNone(ts.num_samples)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data(self):
        def generator_factory():
            return (i for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts = self._create_time_series_with_data(data)
        with self.assertWarnsWith(
            UserWarning,
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__",
        ):
            self.assertIsNone(ts.num_samples)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_data_arr(self):
        def generator_factory():
            return (np.array([i, i + 1]) for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts = self._create_time_series_with_data(data)
        with self.assertWarnsWith(
            UserWarning,
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__",
        ):
            self.assertIsNone(ts.num_samples)
        for xi, yi in zip(data, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dataio_list_timestamps(self):
        length = 100
        data = list(range(length))
        ts = self._create_time_series_with_data(data)
        self.assertEqual(ts.num_samples, length)
        assert data == list(ts.data)

    def _create_time_series_with_timestamps(self, timestamps):
        # data has no __len__ for these tests
        def generator_factory():
            return (i for i in range(100))

        ts = TimeSeries(
            name="test_ts1",
            data=DataChunkIterator(data=generator_factory()),
            unit="grams",
            timestamps=timestamps,
        )
        return ts

    def test_dataio_dci_timestamps(self):
        def generator_factory():
            return (i for i in range(100))

        timestamps = H5DataIO(DataChunkIterator(data=generator_factory()))
        ts = self._create_time_series_with_timestamps(timestamps)
        with self.assertWarns(UserWarning) as record:
            self.assertIsNone(ts.num_samples)
        assert len(record.warnings) == 2
        assert record.warnings[0].message.args[0] == (
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__"
        )
        assert record.warnings[1].message.args[0] == (
            "The timestamps attribute on this TimeSeries (named: test_ts1) has a "
            "__len__, but it cannot be read"
        )
        for xi, yi in zip(timestamps, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_timestamps(self):
        def generator_factory():
            return (i for i in range(100))

        timestamps = DataChunkIterator(data=generator_factory())
        ts = self._create_time_series_with_timestamps(timestamps)
        with self.assertWarns(UserWarning) as record:
            self.assertIsNone(ts.num_samples)
        assert len(record.warnings) == 2
        assert record.warnings[0].message.args[0] == (
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__"
        )
        assert record.warnings[1].message.args[0] == (
            "The timestamps attribute on this TimeSeries (named: test_ts1) has no __len__"
        )
        for xi, yi in zip(timestamps, generator_factory()):
            assert np.allclose(xi, yi)

    def test_dci_timestamps_arr(self):
        def generator_factory():
            return np.array(np.arange(100))

        timestamps = DataChunkIterator(data=generator_factory())
        ts = self._create_time_series_with_timestamps(timestamps)
        with self.assertWarns(UserWarning) as record:
            self.assertIsNone(ts.num_samples)
        assert len(record.warnings) == 2
        assert record.warnings[0].message.args[0] == (
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__"
        )
        assert record.warnings[1].message.args[0] == (
            "The timestamps attribute on this TimeSeries (named: test_ts1) has no __len__"
        )
        for xi, yi in zip(timestamps, generator_factory()):
            assert np.allclose(xi, yi)

    def test_conflicting_time_args(self):
        with self.assertRaisesWith(
            ValueError, "Specifying rate and timestamps is not supported."
        ):
            TimeSeries(
                name="test_ts2",
                data=[10, 11, 12],
                unit="grams",
                rate=30.0,
                timestamps=[0.3, 0.4, 0.5],
            )
        with self.assertRaisesWith(
            ValueError, "Specifying starting_time and timestamps is not supported."
        ):
            TimeSeries(
                name="test_ts2",
                data=[10, 11, 12],
                unit="grams",
                starting_time=30.0,
                timestamps=[0.3, 0.4, 0.5],
            )

    def test_dimension_warning(self):
        msg = (
            "TimeSeries 'test_ts2': Length of data does not match length of timestamps. Your data may be "
            "transposed. Time should be on the 0th dimension"
        )
        with self.assertWarnsWith(UserWarning, msg):
            TimeSeries(
                name="test_ts2",
                data=[10, 11, 12],
                unit="grams",
                timestamps=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            )

    def test_get_timestamps(self):
        time_series = mock_TimeSeries(data=[1, 2, 3], rate=40.0, starting_time=30.0)
        assert_array_equal(time_series.get_timestamps(), [30, 30+1/40, 30+2/40])

        time_series = mock_TimeSeries(data=[1, 2, 3], timestamps=[3, 4, 5], rate=None)
        assert_array_equal(time_series.get_timestamps(), [3, 4, 5])

    def test_get_data_in_units(self):
        ts = mock_TimeSeries(data=[1., 2., 3.], conversion=2., offset=3.)
        assert_array_equal(ts.get_data_in_units(), [5., 7., 9.])

        ts = mock_TimeSeries(data=[1., 2., 3.], conversion=2.)
        assert_array_equal(ts.get_data_in_units(), [2., 4., 6.])

        ts = mock_TimeSeries(data=[1., 2., 3.])
        assert_array_equal(ts.get_data_in_units(), [1., 2., 3.])

    def test_non_positive_rate(self):
        with self.assertRaisesWith(ValueError, 'Rate must not be a negative value.'):
            TimeSeries(name='test_ts', data=list(), unit='volts', rate=-1.0)

        with self.assertWarnsWith(UserWarning,
                                  'Timeseries has a rate of 0.0 Hz, but the length of the data is greater than 1.'):
            TimeSeries(name='test_ts1', data=[1, 2, 3], unit='volts', rate=0.0)

    def test_file_with_non_positive_rate_in_construct_mode(self):
        """Test that UserWarning is raised when rate is 0 or negative
         while being in construct mode (i.e,. on data read)."""
        obj = TimeSeries.__new__(TimeSeries,
                                 container_source=None,
                                 parent=None,
                                 object_id="test",
                                 in_construct_mode=True)
        with self.assertWarnsWith(warn_type=UserWarning, exc_msg='Rate must not be a negative value.'):
            obj.__init__(
                name="test_ts",
                data=list(),
                unit="volts",
                rate=-1.0
            )

    def test_file_with_rate_and_timestamps_in_construct_mode(self):
        """Test that UserWarning is raised when rate and timestamps are both specified
         while being in construct mode (i.e,. on data read)."""
        obj = TimeSeries.__new__(TimeSeries,
                                 container_source=None,
                                 parent=None,
                                 object_id="test",
                                 in_construct_mode=True)
        with self.assertWarnsWith(warn_type=UserWarning, exc_msg='Specifying rate and timestamps is not supported.'):
            obj.__init__(
                name="test_ts",
                data=[11, 12, 13, 14, 15],
                unit="volts",
                rate=1.0,
                timestamps=[1, 2, 3, 4, 5]
            )

    def test_file_with_starting_time_and_timestamps_in_construct_mode(self):
        """Test that UserWarning is raised when starting_time and timestamps are both specified
         while being in construct mode (i.e,. on data read)."""
        obj = TimeSeries.__new__(TimeSeries,
                                 container_source=None,
                                 parent=None,
                                 object_id="test",
                                 in_construct_mode=True)
        with self.assertWarnsWith(warn_type=UserWarning,
                                  exc_msg='Specifying starting_time and timestamps is not supported.'):
            obj.__init__(
                name="test_ts",
                data=[11, 12, 13, 14, 15],
                unit="volts",
                starting_time=1.0,
                timestamps=[1, 2, 3, 4, 5]
            )

    def test_repr_html(self):
        """ Test that html representation of linked timestamp data will occur as expected and will not cause a
        RecursionError
        """
        data1 = [0, 1, 2, 3]
        data2 = [4, 5, 6, 7]
        timestamps = [0.0, 0.1, 0.2, 0.3]
        ts1 = TimeSeries(name="test_ts1", data=data1, unit="grams", timestamps=timestamps)
        ts2 = TimeSeries(name="test_ts2", data=data2, unit="grams", timestamps=ts1)
        pm = ProcessingModule(name="processing", description="a test processing module")
        pm.add(ts1)
        pm.add(ts2)
        self.assertIn('(link to processing/test_ts1/timestamps)', pm._repr_html_())


class TestImage(TestCase):
    def test_init(self):
        im = Image(name="test_image", data=np.ones((10, 10)))
        assert im.name == "test_image"
        assert np.all(im.data == np.ones((10, 10)))


class TestImages(TestCase):

    def test_images(self):
        image1 = Image(name='test_image1', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        assert images.name == "images_name"
        assert images.images == dict(test_image1=image1, test_image2=image2)
        self.assertIs(images.order_of_images[0], image2)
        self.assertIs(images.order_of_images[1], image1)


class TestTimeSeriesReferenceVectorData(TestCase):
    def _create_time_series_with_rate(self):
        ts = TimeSeries(
            name="test",
            description="test",
            data=np.arange(10),
            unit="unit",
            starting_time=5.0,
            rate=0.1,
        )
        return ts

    def _create_time_series_with_timestamps(self):
        ts = TimeSeries(
            name="test",
            description="test",
            data=np.arange(10),
            unit="unit",
            timestamps=np.arange(10.0),
        )
        return ts

    def test_init(self):
        temp = TimeSeriesReferenceVectorData()
        self.assertEqual(temp.name, "timeseries")
        self.assertEqual(
            temp.description,
            "Column storing references to a TimeSeries (rows). For each TimeSeries this "
            "VectorData column stores the start_index and count to indicate the range in time "
            "to be selected as well as an object reference to the TimeSeries.",
        )
        self.assertListEqual(temp.data, [])
        temp = TimeSeriesReferenceVectorData(name="test", description="test")
        self.assertEqual(temp.name, "test")
        self.assertEqual(temp.description, "test")

    def test_get_empty(self):
        """Get data from an empty TimeSeriesReferenceVectorData"""
        temp = TimeSeriesReferenceVectorData()
        self.assertListEqual(temp[:], [])
        with self.assertRaises(IndexError):
            temp[0]

    def test_append_get_length1_valid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with one element and valid data"""
        temp = TimeSeriesReferenceVectorData()
        value = TimeSeriesReference(0, 5, self._create_time_series_with_rate())
        temp.append(value)
        self.assertTupleEqual(temp[0], value)
        self.assertListEqual(
            temp[:],
            [
                TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*value),
            ],
        )

    def test_add_row_get_length1_valid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with one element and valid data"""
        temp = TimeSeriesReferenceVectorData()
        value = TimeSeriesReference(0, 5, self._create_time_series_with_rate())
        temp.add_row(value)
        self.assertTupleEqual(temp[0], value)
        self.assertListEqual(
            temp[:],
            [
                TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*value),
            ],
        )

    def test_get_length1_invalid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with one element and invalid data"""
        temp = TimeSeriesReferenceVectorData()
        value = TimeSeriesReference(-1, -1, self._create_time_series_with_rate())
        temp.append(value)
        # test index slicing
        re = temp[0]
        self.assertTrue(
            isinstance(re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE)
        )
        self.assertTupleEqual(
            re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE
        )
        # test array slicing and list slicing
        selection = [
            slice(None),
            [
                0,
            ],
        ]
        for s in selection:
            re = temp[s]
            self.assertTrue(isinstance(re, list))
            self.assertTrue(len(re), 1)
            self.assertTrue(
                isinstance(
                    re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE
                )
            )
            self.assertTupleEqual(
                re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE
            )

    def test_get_length5_valid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with 5 elements"""
        temp = TimeSeriesReferenceVectorData()
        num_values = 5
        values = [
            TimeSeriesReference(0, 5, self._create_time_series_with_rate())
            for i in range(num_values)
        ]
        for v in values:
            temp.append(v)
        # Test single element selection
        for i in range(num_values):
            # test index slicing
            re = temp[i]
            self.assertTupleEqual(re, values[i])
            # test slicing
            re = temp[i : i + 1]
            self.assertTupleEqual(
                re[0],
                TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[i]),
            )
        # Test multi element selection
        re = temp[0:2]
        self.assertTupleEqual(
            re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[0])
        )
        self.assertTupleEqual(
            re[1], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[1])
        )

    def test_get_length5_with_invalid_data(self):
        """Get data from a TimeSeriesReferenceVectorData with 5 elements"""
        temp = TimeSeriesReferenceVectorData()
        num_values = 5
        values = [
            TimeSeriesReference(0, 5, self._create_time_series_with_rate())
            for i in range(num_values - 2)
        ]
        values = (
            [
                TimeSeriesReference(-1, -1, self._create_time_series_with_rate()),
            ]
            + values
            + [
                TimeSeriesReference(-1, -1, self._create_time_series_with_rate()),
            ]
        )
        for v in values:
            temp.append(v)
        # Test single element selection
        for i in range(num_values):
            # test index slicing
            re = temp[i]
            if i in [0, 4]:
                self.assertTrue(
                    isinstance(
                        re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE
                    )
                )
                self.assertTupleEqual(
                    re, TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE
                )
            else:
                self.assertTupleEqual(re, values[i])
            # test slicing
            re = temp[i : i + 1]
            if i in [0, 4]:
                self.assertTrue(
                    isinstance(
                        re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE
                    )
                )
                self.assertTupleEqual(
                    re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE
                )
            else:
                self.assertTupleEqual(
                    re[0],
                    TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(
                        *values[i]
                    ),
                )
        # Test multi element selection
        re = temp[0:2]
        self.assertTupleEqual(
            re[0], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_NONE_TYPE
        )
        self.assertTupleEqual(
            re[1], TimeSeriesReferenceVectorData.TIME_SERIES_REFERENCE_TUPLE(*values[1])
        )

    def test_add_row(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = TimeSeriesReference(0, 5, TimeSeries(name='test', description='test',
                                                   data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        v.add_row(val)
        self.assertTupleEqual(v[0], val)

    def test_add_row_with_plain_tuple(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = (0, 5, TimeSeries(name='test', description='test',
                                data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        v.add_row(val)
        self.assertTupleEqual(v[0], val)

    def test_add_row_with_bad_tuple(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = (0.0, 5, TimeSeries(name='test', description='test',
                                  data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(TypeError, "idx_start must be an integer not <class 'float'>"):
            v.add_row(val)

    def test_add_row_restricted_type(self):
        v = TimeSeriesReferenceVectorData(name="a", description="a")
        with self.assertRaisesWith(
            TypeError,
            "TimeSeriesReferenceVectorData.add_row: incorrect type for "
            "'val' (got 'int', expected 'TimeSeriesReference or tuple')",
        ):
            v.add_row(1)

    def test_append(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = TimeSeriesReference(0, 5, TimeSeries(name='test', description='test',
                                                   data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        v.append(val)
        self.assertTupleEqual(v[0], val)

    def test_append_with_plain_tuple(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = (0, 5, TimeSeries(name='test', description='test',
                                data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        v.append(val)
        self.assertTupleEqual(v[0], val)

    def test_append_with_bad_tuple(self):
        v = TimeSeriesReferenceVectorData(name='a', description='a')
        val = (0.0, 5, TimeSeries(name='test', description='test',
                                  data=np.arange(10), unit='unit', starting_time=5.0, rate=0.1))
        with self.assertRaisesWith(TypeError, "idx_start must be an integer not <class 'float'>"):
            v.append(val)

    def test_append_restricted_type(self):
        v = TimeSeriesReferenceVectorData(name="a", description="a")
        with self.assertRaisesWith(
            TypeError,
            "TimeSeriesReferenceVectorData.append: incorrect type for "
            "'arg' (got 'float', expected 'TimeSeriesReference or tuple')",
        ):
            v.append(2.0)


class TestTimeSeriesReference(TestCase):
    def _create_time_series_with_rate(self):
        ts = TimeSeries(
            name="test",
            description="test",
            data=np.arange(10),
            unit="unit",
            starting_time=5.0,
            rate=0.1,
        )
        return ts

    def _create_time_series_with_timestamps(self):
        ts = TimeSeries(
            name="test",
            description="test",
            data=np.arange(10),
            unit="unit",
            timestamps=np.arange(10.0),
        )
        return ts

    def test_check_types(self):
        # invalid selection but with correct types
        tsr = TimeSeriesReference(-1, -1, self._create_time_series_with_rate())
        self.assertTrue(tsr.check_types())
        # invalid types, use float instead of int for both idx_start and count
        tsr = TimeSeriesReference(1.0, 5.0, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            TypeError, "idx_start must be an integer not <class 'float'>"
        ):
            tsr.check_types()
        # invalid types, use float instead of int for idx_start only
        tsr = TimeSeriesReference(1.0, 5, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            TypeError, "idx_start must be an integer not <class 'float'>"
        ):
            tsr.check_types()
        # invalid types, use float instead of int for count only
        tsr = TimeSeriesReference(1, 5.0, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            TypeError, "count must be an integer <class 'float'>"
        ):
            tsr.check_types()
        # invalid type for TimeSeries but valid idx_start and count
        tsr = TimeSeriesReference(1, 5, None)
        with self.assertRaisesWith(
            TypeError, "timeseries must be of type TimeSeries. <class 'NoneType'>"
        ):
            tsr.check_types()

    def test_is_invalid(self):
        tsr = TimeSeriesReference(-1, -1, self._create_time_series_with_rate())
        self.assertFalse(tsr.isvalid())

    def test_is_valid(self):
        tsr = TimeSeriesReference(0, 10, self._create_time_series_with_rate())
        self.assertTrue(tsr.isvalid())

    def test_is_valid_bad_index(self):
        # Error: negative start_index but positive count
        tsr = TimeSeriesReference(-1, 10, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'idx_start' -1 out of range for timeseries 'test'"
        ):
            tsr.isvalid()
        # Error: start_index too large
        tsr = TimeSeriesReference(10, 0, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'idx_start' 10 out of range for timeseries 'test'"
        ):
            tsr.isvalid()
        # Error: positive start_index but negative count
        tsr = TimeSeriesReference(0, -3, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'count' -3 invalid. 'count' must be positive"
        ):
            tsr.isvalid()
        # Error:  start_index + count too large
        tsr = TimeSeriesReference(3, 10, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'idx_start + count' out of range for timeseries 'test'"
        ):
            tsr.isvalid()

    def test_is_valid_no_num_samples(self):
        def generator_factory():
            return (i for i in range(100))

        data = DataChunkIterator(data=generator_factory())
        ts = TimeSeries(name="test_ts1", data=data, unit="grams", rate=0.1)
        tsr = TimeSeriesReference(0, 10, ts)
        with self.assertWarnsWith(
            UserWarning,
            "The data attribute on this TimeSeries (named: test_ts1) has no __len__",
        ):
            self.assertTrue(tsr.isvalid())

    def test_timestamps_property(self):
        # Timestamps from starting_time and rate
        tsr = TimeSeriesReference(5, 4, self._create_time_series_with_rate())
        np.testing.assert_array_equal(tsr.timestamps, np.array([5.5, 5.6, 5.7, 5.8]))
        # Timestamps from timestamps directly
        tsr = TimeSeriesReference(5, 4, self._create_time_series_with_timestamps())
        np.testing.assert_array_equal(tsr.timestamps, np.array([5.0, 6.0, 7.0, 8.0]))

    def test_timestamps_property_invalid_reference(self):
        # Timestamps from starting_time and rate
        tsr = TimeSeriesReference(-1, -1, self._create_time_series_with_rate())
        self.assertIsNone(tsr.timestamps)

    def test_timestamps_property_bad_reference(self):
        tsr = TimeSeriesReference(0, 12, self._create_time_series_with_timestamps())
        with self.assertRaisesWith(
            IndexError, "'idx_start + count' out of range for timeseries 'test'"
        ):
            tsr.timestamps
        tsr = TimeSeriesReference(0, 12, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'idx_start + count' out of range for timeseries 'test'"
        ):
            tsr.timestamps

    def test_data_property(self):
        tsr = TimeSeriesReference(5, 4, self._create_time_series_with_rate())
        np.testing.assert_array_equal(tsr.data, np.array([5.0, 6.0, 7.0, 8.0]))

    def test_data_property_invalid_reference(self):
        tsr = TimeSeriesReference(-1, -1, self._create_time_series_with_rate())
        self.assertIsNone(tsr.data)

    def test_data_property_bad_reference(self):
        tsr = TimeSeriesReference(0, 12, self._create_time_series_with_rate())
        with self.assertRaisesWith(
            IndexError, "'idx_start + count' out of range for timeseries 'test'"
        ):
            tsr.data

    def test_empty_reference_creation(self):
        tsr = TimeSeriesReference.empty(self._create_time_series_with_rate())
        self.assertFalse(tsr.isvalid())
        self.assertIsNone(tsr.data)
        self.assertIsNone(tsr.timestamps)
