import unittest2 as unittest

from pynwb.core import DynamicTable, TableColumn


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
        table = DynamicTable("with_table_columns", 'PyNWB unit test', columns=cols)
        return table

    def with_spec(self):
        table = DynamicTable("with_spec", 'PyNWB unit test', columns=self.spec)
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
        self.assertEqual(table.ids.data, [0, 1, 2, 3, 4])

    def test_constructor_ids_default(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_spec", 'PyNWB unit test', columns=columns)
        self.check_table(table)

    def test_constructor_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        table = DynamicTable("with_columns", 'PyNWB unit test', ids=[0, 1, 2, 3, 4], columns=columns)
        self.check_table(table)

    def test_constructor_ids_bad_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d)
                   for s, d in zip(self.spec, self.data)]
        msg = "must provide same number of ids as length of columns if specifying ids"
        with self.assertRaisesRegex(ValueError, msg):
            DynamicTable("with_columns", 'PyNWB unit test', ids=[0, 1], columns=columns)

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
        self.assertTrue(hasattr(row, 'dtype'))
        self.assertEqual(row.dtype.names, ('ids', 'foo', 'bar', 'baz'))
        self.assertEqual(row['foo'], 3)
        self.assertEqual(row['bar'], 30.0)
        self.assertEqual(row['baz'], b'bird')

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
        self.assertTrue(hasattr(row, 'dtype'))
        self.assertEqual(row.dtype.names, ('ids', 'foo', 'bar', 'baz'))

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
