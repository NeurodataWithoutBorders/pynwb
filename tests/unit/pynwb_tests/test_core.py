import unittest2 as unittest

from pynwb.core import DynamicTable, VectorData, ElementIdentifiers, NWBTable
from pynwb import NWBFile, TimeSeries

import pandas as pd
from datetime import datetime
from dateutil.tz import tzlocal


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
        cols = [VectorData(**d) for d in self.spec]
        table = DynamicTable("with_table_columns", 'a test table', columns=cols)
        return table

    def with_columns_and_data(self):
        columns = [
            VectorData(name=s['name'], description=s['description'], data=d)
            for s, d in zip(self.spec, self.data)
        ]
        return DynamicTable("with_columns_and_data", 'a test table', columns=columns)

    def with_spec(self):
        table = DynamicTable("with_spec", 'a test table', columns=self.spec)
        return table

    def check_empty_table(self, table):
        self.assertIsInstance(table.columns[0], VectorData)
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
        columns = [VectorData(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_spec", 'a test table', columns=columns)
        self.check_table(table)

    def test_constructor_ids(self):
        columns = [VectorData(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_columns", 'a test table', id=[0, 1, 2, 3, 4], columns=columns)
        self.check_table(table)

    def test_constructor_ElementIdentifier_ids(self):
        columns = [VectorData(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        ids = ElementIdentifiers('ids', [0, 1, 2, 3, 4])
        table = DynamicTable("with_columns", 'a test table', id=ids, columns=columns)
        self.check_table(table)

    def test_constructor_ids_bad_ids(self):
        columns = [VectorData(name=s['name'], description=s['description'], data=d)
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


class TestNWBTable(unittest.TestCase):

    def setUp(self):
        class MyTable(NWBTable):
            __columns__ = [
                {'name': 'foo', 'type': str, 'doc': 'the foo column'},
                {'name': 'bar', 'type': int, 'doc': 'the bar column'},
            ]
        self.cls = MyTable

    def basic_data(self):
        return [
            [1, 'a'],
            [2, 'b'],
            [3, 'c']
        ]

    def table_with_data(self):
        return self.cls(
            name='testing table',
            data=self.basic_data()
        )

    def test_init(self):
        table = self.table_with_data()
        assert(table['foo', 1]) == 2

    def test_to_dataframe(self):
        obtained = self.table_with_data().to_dataframe()
        expected = pd.DataFrame({
            'foo': [1, 2, 3],
            'bar': ['a', 'b', 'c']
        })

        assert expected.equals(obtained)

    def test_from_dataframe(self):
        df = pd.DataFrame({
            'bar': ['a', 'b', 'c']
        }, index=pd.Index(name='foo', data=[1, 2, 3], dtype=int))
        table = self.cls.from_dataframe(df=df, name='test table')

        assert table['foo', 1] == 2

    def test_dataframe_roundtrip(self):
        expected = pd.DataFrame({
            'foo': [1, 2, 3],
            'bar': ['a', 'b', 'c']
        })
        obtained = self.cls.from_dataframe(df=expected, name='test table').to_dataframe()
        assert expected.equals(obtained)

    def test_from_dataframe_missing_columns(self):
        df = pd.DataFrame({
            'bar': ['a', 'b', 'c']
        })

        with self.assertRaises(ValueError):
            self.cls.from_dataframe(df=df, name='test_table')

    def test_from_dataframe_extra_columns(self):
        df = pd.DataFrame({
            'foo': [1, 2, 3],
            'bar': ['a', 'b', 'c'],
            'baz': [-1, -2, -3]
        })

        with self.assertRaises(ValueError):
            self.cls.from_dataframe(df=df, name='test_table')


class TestPrint(unittest.TestCase):

    def test_print_file(self):
        nwbfile = NWBFile(session_description='session_description',
                          identifier='identifier', session_start_time=datetime.now(tzlocal()))
        ts = TimeSeries('name', [1., 2., 3.] * 1000, timestamps=[1, 2, 3])
        ts2 = TimeSeries('name2', [1, 2, 3] * 1000, timestamps=[1, 2, 3])
        self.assertEqual(str(ts), """
name <class 'pynwb.base.TimeSeries'>
Fields:
  comments: no comments
  conversion: 1.0
  data: [1. 2. 3. ... 1. 2. 3.]
  description: no description
  interval: 1
  num_samples: 3000
  resolution: 0.0
  timestamps: [1 2 3]
  timestamps_unit: Seconds
"""
                         )
        nwbfile.add_acquisition(ts)
        nwbfile.add_acquisition(ts2)
        empty_set_str = str(set())  # changes between py2 and py3
        self.assertEqual(str(nwbfile),
                         """
root <class 'pynwb.file.NWBFile'>
Fields:
  acquisition: { name <class 'pynwb.base.TimeSeries'>,  name2 <class 'pynwb.base.TimeSeries'> }
  analysis: { }
  devices: { }
  electrode_groups: { }
  epoch_tags: """ + empty_set_str + """
  ic_electrodes: { }
  imaging_planes: { }
  modules: { }
  ogen_sites: { }
  stimulus: { }
  stimulus_template: { }
  time_intervals: { }
""")
