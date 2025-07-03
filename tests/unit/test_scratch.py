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
            description='test scratch',
        )
        self.assertEqual(sd.name, 'foo')
        self.assertListEqual(sd.data, [1, 2, 3, 4])
        self.assertEqual(sd.description, 'test scratch')

    def test_scratch_notes_deprecation(self):
        msg = ("The `notes` argument of ScratchData.__init__ has been deprecated and will "
               "be removed in PyNWB 4.0. Use description instead.")
        with self.assertRaisesWith(ValueError, msg):
            ScratchData(name='test', data=[1, 2, 3, 4, 5], notes='test notes')

        # create object in construct mode, modeling the behavior of the ObjectMapper on read 
        # should not raise error or warning
        data = ScratchData.__new__(ScratchData, in_construct_mode=True)
        data.__init__(name='test', data=[1, 2, 3, 4, 5], notes='test notes')
        self.assertEqual(data.description, 'test notes')

        # test notes property
        msg = ("Use of ScratchData.notes has been deprecated and will be removed in PyNWB 4.0. "
               "Use ScratchData.description instead.")
        
        with self.assertWarnsWith(DeprecationWarning, msg):
            data.notes

        # test notes setter
        data = ScratchData(name='test', data=[1, 2, 3, 4, 5], description='test description')
        with self.assertRaisesWith(ValueError, msg):
            data.notes = 'test notes'

    def test_scratch_no_description(self):
        with self.assertRaisesWith(ValueError, 'ScratchData.description is required.'):
            ScratchData(name='test', data=[1, 2, 3, 4, 5])

    def test_scratch_notes_and_description(self):
        msg = ('Cannot provide both notes and description to ScratchData.__init__. The description '
               'argument is recommended.')
        data = ScratchData.__new__(ScratchData, in_construct_mode=True)
        with self.assertRaisesWith(ValueError, msg):
            data.__init__(name='test', data=[1, 2, 3, 4, 5], notes='test notes',
                          description='test description')

    def test_add_scratch_int(self):
        ret = self.nwbfile.add_scratch(2, name='test', description='test data')
        self.assertIsInstance(ret, ScratchData)
        self.assertEqual(ret.name, 'test')
        self.assertEqual(ret.data, 2)
        self.assertEqual(ret.description, 'test data')
        self.assertIs(ret.parent, self.nwbfile)
        self.assertEqual(self.nwbfile.get_scratch('test'), 2)

    def test_add_scratch_list(self):
        self.nwbfile.add_scratch([1, 2, 3, 4], name='test', description='test data')
        assert_array_equal(self.nwbfile.get_scratch('test'), np.array([1, 2, 3, 4]))

    def test_add_scratch_ndarray(self):
        self.nwbfile.add_scratch(np.array([1, 2, 3, 4]), name='test', description='test data')
        assert_array_equal(self.nwbfile.get_scratch('test'), np.array([1, 2, 3, 4]))

    def test_add_scratch_list_no_name(self):
        msg = ('A name is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
               'list, tuple, or pandas.DataFrame as scratch data.')
        with self.assertRaisesWith(ValueError, msg):
            self.nwbfile.add_scratch([1, 2, 3, 4])

    def test_add_scratch_ndarray_no_description(self):
        msg = ('A description is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
               'list, tuple, or pandas.DataFrame as scratch data.')
        with self.assertRaisesWith(ValueError, msg):
            self.nwbfile.add_scratch(np.array([1, 2, 3, 4]), name='test')

    def test_add_scratch_dataframe(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.nwbfile.add_scratch(data, name='test', description='my_table')
        assert_array_equal(data.values, self.nwbfile.get_scratch('test').values)
        assert_array_equal(data.index.values, self.nwbfile.get_scratch('test').index.values)

    def test_add_scratch_dataframe_no_description(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        msg = ('A description is required for NWBFile.add_scratch when adding a scalar, numpy.ndarray, '
               'list, tuple, or pandas.DataFrame as scratch data.')
        with self.assertRaisesWith(ValueError, msg):
            self.nwbfile.add_scratch(data, name='test')

    def test_add_scratch_notes_and_description(self):
        error_msg = 'Cannot call add_scratch with (notes or table_description) and description'
        warning_msg = ("Use of the `notes` or `table_description` argument is deprecated and will be "
                       "removed in PyNWB 4.0. Use the `description` argument instead.")
        with self.assertWarnsWith(DeprecationWarning, warning_msg):
            with self.assertRaisesWith(ValueError, error_msg):
                self.nwbfile.add_scratch([1, 2, 3, 4], name='test', description='test data', notes='test notes')

    def test_add_scratch_container(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        self.nwbfile.add_scratch(data)
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_add_scratch_container_name(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        msg = ('The name argument is ignored when adding an NWBContainer, ScratchData, or '
               'DynamicTable to scratch.')
        with self.assertWarnsWith(UserWarning, msg):
            self.nwbfile.add_scratch(data, name='Foo')
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_add_scratch_container_description(self):
        data = TimeSeries(name='test_ts', data=[1, 2, 3, 4, 5], unit='unit', timestamps=[1.1, 1.2, 1.3, 1.4, 1.5])
        msg = ('The description argument is ignored when adding an NWBContainer, ScratchData, or '
               'DynamicTable to scratch.')
        with self.assertWarnsWith(UserWarning, msg):
            self.nwbfile.add_scratch(data, description='test scratch')
        self.assertIs(self.nwbfile.get_scratch('test_ts'), data)
        self.assertIs(self.nwbfile.scratch['test_ts'], data)

    def test_add_scratch_scratchdata(self):
        data = ScratchData(name='test', data=[1, 2, 3, 4, 5], description='test description')
        self.nwbfile.add_scratch(data)
        self.assertIs(data.parent, self.nwbfile)
        self.assertIs(self.nwbfile.get_scratch('test', convert=False), data)
        self.assertIs(self.nwbfile.scratch['test'], data)

    def test_add_scratch_dynamictable(self):
        data = DynamicTable(name='test', description='description')
        self.nwbfile.add_scratch(data)
        self.assertIs(self.nwbfile.get_scratch('test', convert=False), data)
        self.assertIs(self.nwbfile.scratch['test'], data)
    
    def test_add_scratch_notes_deprecation(self):
        msg =  ("Use of the `notes` or `table_description` argument is deprecated and will be removed in PyNWB 4.0. "
                "Use the `description` argument instead.")
        with self.assertWarnsWith(DeprecationWarning, msg):
            self.nwbfile.add_scratch(name='test', data=[1, 2, 3, 4, 5], notes='test notes')
        self.assertEqual(self.nwbfile.scratch['test'].description, 'test notes')    

    def test_add_scratch_table_description_deprecation(self):
        msg =  ('Use of the `notes` or `table_description` argument is deprecated and will be removed in PyNWB 4.0. '
                'Use the `description` argument instead.')
        df = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        with self.assertWarnsWith(DeprecationWarning, msg):
            self.nwbfile.add_scratch(name='test', data=df,
                                     table_description='test table_description')
        self.assertEqual(self.nwbfile.scratch['test'].description, 'test table_description')    

    def test_get_scratch_list_convert_false(self):
        self.nwbfile.add_scratch([1, 2, 3, 4], name='test', description='test description')
        self.assertTrue(isinstance(self.nwbfile.get_scratch('test', convert=False), ScratchData))
        self.assertTrue(isinstance(self.nwbfile.scratch['test'], ScratchData))
        self.assertEqual(self.nwbfile.scratch['test'].data, [1, 2, 3, 4])

    def test_get_scratch_df_convert_false(self):
        data = pd.DataFrame(data={'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})
        self.nwbfile.add_scratch(data, name='test', description='my_table')
        self.assertTrue(isinstance(self.nwbfile.get_scratch('test', convert=False), DynamicTable))
        self.assertTrue(isinstance(self.nwbfile.scratch['test'], DynamicTable))
        self.assertEqual(self.nwbfile.scratch['test'].description, 'my_table')
