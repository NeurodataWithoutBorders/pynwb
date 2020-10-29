from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd

from pynwb import NWBFile, TimeSeries
from pynwb.core import ScratchData, DynamicTable
from pynwb.testing import TestCase


class TestScratchData(TestCase):

    def setUp(self):
        self.nwbfile = NWBFile(
            session_description='a file to test writing and reading scratch data',
            identifier='TEST_scratch',
            session_start_time=datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        )

    def test_constructor_list(self):
        sd = ScratchData(
            name='foo',
            data=[1, 2, 3, 4],
            notes='test scratch',
        )
        self.assertEqual(sd.name, 'foo')
        self.assertListEqual(sd.data, [1, 2, 3, 4])
        self.assertEqual(sd.notes, 'test scratch')

    def test_add_scratch_list(self):
        self.nwbfile.add_scratch([1, 2, 3, 4], name='test')
        assert_array_equal(self.nwbfile.get_scratch('test'), np.array([1, 2, 3, 4]))

    def test_add_scratch_ndarray(self):
        self.nwbfile.add_scratch(np.array([1, 2, 3, 4]), name='test')
        assert_array_equal(self.nwbfile.get_scratch('test'), np.array([1, 2, 3, 4]))

    def test_add_scratch_list_no_name(self):
        msg = 'please provide a name for scratch data'
        with self.assertRaisesWith(ValueError, msg):
            self.nwbfile.add_scratch([1, 2, 3, 4])

    def test_add_scratch_dataframe(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.nwbfile.add_scratch(data, name='test')
        assert_array_equal(data.values, self.nwbfile.get_scratch('test').values)
        assert_array_equal(data.index.values, self.nwbfile.get_scratch('test').index.values)

    def test_add_scratch_dataframe_description(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.nwbfile.add_scratch(data, name='test', table_description='my_table')
        assert_array_equal(data.values, self.nwbfile.get_scratch('test').values)
        assert_array_equal(data.index.values, self.nwbfile.get_scratch('test').index.values)

    def test_add_scratch_dataframe_notes(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        warn_msg = 'Notes argument is ignored when adding a pandas DataFrame to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            self.nwbfile.add_scratch(data, name='test', notes='my notes')

    def test_add_scratch_container(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        self.nwbfile.add_scratch(data)
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_scratch_container_with_name(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        warn_msg = 'Name argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            self.nwbfile.add_scratch(data, name='Foo')
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_scratch_container_with_notes(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        warn_msg = 'Notes argument is ignored when adding an NWBContainer to scratch'
        with self.assertWarnsWith(UserWarning, warn_msg):
            self.nwbfile.add_scratch(data, notes='test scratch')
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_get_scratch_list_convert_false(self):
        self.nwbfile.add_scratch([1, 2, 3, 4], name='test')
        self.assertTrue(isinstance(self.nwbfile.get_scratch('test', convert=False), ScratchData))
        self.assertTrue(isinstance(self.nwbfile.scratch['test'], ScratchData))
        self.assertEqual(self.nwbfile.scratch['test'].data, [1, 2, 3, 4])

    def test_get_scratch_df_convert_false(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.nwbfile.add_scratch(data, name='test', table_description='my_table')
        self.assertTrue(isinstance(self.nwbfile.get_scratch('test', convert=False), DynamicTable))
        self.assertTrue(isinstance(self.nwbfile.scratch['test'], DynamicTable))
        self.assertEqual(self.nwbfile.scratch['test'].description, 'my_table')
