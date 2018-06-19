import unittest2 as unittest

from pynwb.core import DynamicTable, TableColumn


class TestDynamicTable(unittest.TestCase):

    def setUp(self):
        self.spec = [
            {'name': 'foo', 'description': 'foo column'},
            {'name': 'bar', 'description': 'bar column'},
            {'name': 'baz', 'description': 'baz column'}
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
        self.assertEqual(table.columns[0].data, [1, 2])
        self.assertEqual(table.columns[1].data, [10.0, 20.0])
        self.assertEqual(table.columns[2].data, ['cat', 'dog'])
        self.assertEqual(table.ids.data, [0, 1])

    def test_constructor_ids_default(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d) for s, d in
                                zip(self.spec, ([1, 2], [10.0, 20.0], ['cat', 'dog']))]
        table = DynamicTable("with_spec", 'PyNWB unit test', columns=columns)
        self.check_table(table)

    def test_constructor_ids(self):
        columns = [TableColumn(name=s['name'], description=s['description'], data=d) for s, d in
                                zip(self.spec, ([1, 2], [10.0, 20.0], ['cat', 'dog']))]
        table = DynamicTable("with_columns", 'PyNWB unit test', ids=[0, 1], columns=columns)
        self.check_table(table)

    def add_rows(self, table):
        table.add_row({'foo': 1, 'bar': 10.0, 'baz': 'cat'})
        table.add_row({'foo': 2, 'bar': 20.0, 'baz': 'dog'})

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
