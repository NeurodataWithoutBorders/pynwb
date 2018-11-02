from datetime import datetime

import numpy as np
import pandas as pd
import unittest2 as unittest
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.base import ProcessingModule, TimeSeries, Images, Image, DynamicTable, TableColumn, ElementIdentifiers
from pynwb.form.backends.hdf5 import H5DataIO
from pynwb.form.data_utils import DataChunkIterator


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


class TestDynamicTable(unittest.TestCase):

    def setUp(self):
        self.spec = [
            {'name': 'foo', 'description': 'foo column'},
            {'name': 'bar', 'description': 'bar column'},
            {'name': 'baz', 'description': 'baz column'}
        ]
        self.data = [
            [1, 2, 3, 4, 5],
            [10.0, 20.0, 30.0, 40.0, 50.0],
            ['cat', 'dog', 'bird', 'fish', 'lizard']
        ]

    def with_table_columns(self):
        cols = [TableColumn(**d) for d in self.spec]
        table = DynamicTable("with_table_columns", 'a test table', columns=cols)
        return table

    def with_columns_and_data(self):
        columns = [
            TableColumn(name=s['name'], description=s['description'], data=d)
            for s, d in zip(self.spec, self.data)
        ]
        return DynamicTable("with_columns_and_data", 'a test table', columns=columns)

    def with_spec(self):
        table = DynamicTable("with_spec", 'a test table', columns=self.spec)
        return table

    def check_empty_table(self, table):
        self.assertIsInstance(table.columns[0], TableColumn)
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(table.colnames, ('foo', 'bar', 'baz'))

    def test_constructor_table_columns(self):
        table = self.with_table_columns()
        self.assertEqual(table.name, 'with_table_columns')
        self.check_empty_table(table)

    def test_constructor_spec(self):
        table = self.with_spec()
        self.assertEqual(table.name, 'with_spec')
        self.check_empty_table(table)

    def check_table(self, table):
        self.assertEqual(len(table), 5)
        self.assertEqual(table.columns[0].data, [1, 2, 3, 4, 5])
        self.assertEqual(table.columns[1].data, [10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(table.columns[2].data, ['cat', 'dog', 'bird', 'fish', 'lizard'])
        self.assertEqual(table.id.data, [0, 1, 2, 3, 4])

    def test_constructor_ids_default(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_spec", 'a test table', columns=columns)
        self.check_table(table)

    def test_constructor_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_columns", 'a test table', id=[0, 1, 2, 3, 4], columns=columns)
        self.check_table(table)

    def test_constructor_ElementIdentifier_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        ids = ElementIdentifiers('ids', [0, 1, 2, 3, 4])
        table = DynamicTable("with_columns", 'a test table', id=ids, columns=columns)
        self.check_table(table)

    def test_constructor_ids_bad_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        msg = "must provide same number of ids as length of columns"
        with self.assertRaisesRegex(ValueError, msg):
            DynamicTable("with_columns", 'a test table', id=[0, 1], columns=columns)

    def add_rows(self, table):
        table.add_row({'foo': 1, 'bar': 10.0, 'baz': 'cat'})
        table.add_row({'foo': 2, 'bar': 20.0, 'baz': 'dog'})
        table.add_row({'foo': 3, 'bar': 30.0, 'baz': 'bird'})
        table.add_row({'foo': 4, 'bar': 40.0, 'baz': 'fish'})
        table.add_row({'foo': 5, 'bar': 50.0, 'baz': 'lizard'})

    def test_add_row(self):
        table = self.with_spec()
        self.add_rows(table)
        self.check_table(table)

    def test_get_item(self):
        table = self.with_spec()
        self.add_rows(table)
        self.check_table(table)

    def test_add_column(self):
        table = self.with_spec()
        table.add_column(name='qux', description='qux column')
        self.assertEqual(table.colnames, ('foo', 'bar', 'baz', 'qux'))

    def test_getitem_row_num(self):
        table = self.with_spec()
        self.add_rows(table)
        row = table[2]
        self.assertEqual(row[0], 2)
        self.assertEqual(row[1], 3)
        self.assertEqual(row[2], 30.0)
        self.assertEqual(row[3], 'bird')

    def test_getitem_column(self):
        table = self.with_spec()
        self.add_rows(table)
        col = table['bar']
        self.assertEqual(col[0], 10.0)
        self.assertEqual(col[1], 20.0)
        self.assertEqual(col[2], 30.0)
        self.assertEqual(col[3], 40.0)
        self.assertEqual(col[4], 50.0)

    def test_getitem_list_idx(self):
        table = self.with_spec()
        self.add_rows(table)
        row = table[[0, 2, 4]]
        self.assertEqual(len(row), 3)
        self.assertEqual(row[0], (0, 1, 10.0, 'cat'))
        self.assertEqual(row[1], (2, 3, 30.0, 'bird'))
        self.assertEqual(row[2], (4, 5, 50.0, 'lizard'))

    def test_getitem_point_idx_colname(self):
        table = self.with_spec()
        self.add_rows(table)
        val = table[2, 'bar']
        self.assertEqual(val, 30.0)

    def test_getitem_point_idx_colidx(self):
        table = self.with_spec()
        self.add_rows(table)
        val = table[2, 2]
        self.assertEqual(val, 30.0)

    def test_add_to_file(self):
        table = self.with_spec()
        self.add_rows(table)

        nwbfile = NWBFile(session_description='session_description',
                          identifier='identifier', session_start_time=datetime.now(tzlocal()))

        module_behavior = nwbfile.create_processing_module('a', 'b')

        module_behavior.add_container(table)

    def test_pandas_roundtrip(self):
        df = pd.DataFrame({
            'a': [1, 2, 3, 4],
            'b': ['a', 'b', 'c', '4']
        }, index=pd.Index(name='an_index', data=[2, 4, 6, 8]))

        table = DynamicTable.from_dataframe(df, 'foo')
        obtained = table.to_dataframe()

        assert df.equals(obtained)

    def test_to_dataframe(self):
        table = self.with_columns_and_data()
        expected_df = pd.DataFrame({
            'foo': [1, 2, 3, 4, 5],
            'bar': [10.0, 20.0, 30.0, 40.0, 50.0],
            'baz': ['cat', 'dog', 'bird', 'fish', 'lizard']
        })
        obtained_df = table.to_dataframe()
        assert expected_df.equals(obtained_df)

    def test_from_dataframe(self):
        df = pd.DataFrame({
            'foo': [1, 2, 3, 4, 5],
            'bar': [10.0, 20.0, 30.0, 40.0, 50.0],
            'baz': ['cat', 'dog', 'bird', 'fish', 'lizard']
        }).loc[:, ('foo', 'bar', 'baz')]

        obtained_table = DynamicTable.from_dataframe(df, 'test')
        self.check_table(obtained_table)

    def test_missing_columns(self):
        table = self.with_spec()

        with self.assertRaises(ValueError):
            table.add_row({'bar': 60.0, 'foo': [6]}, None)

    def test_extra_columns(self):
        table = self.with_spec()

        with self.assertRaises(ValueError):
            table.add_row({'bar': 60.0, 'foo': 6, 'baz': 'oryx', 'qax': -1}, None)
