import pandas as pd
import unittest2 as unittest
from pynwb.core import NWBTable


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
