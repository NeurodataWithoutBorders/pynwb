import unittest2 as unittest
import os
from h5py import File
import numpy as np

from pynwb.form.query import *  # noqa: F403
from pynwb.form.array import *  # noqa: F403


class AbstractQueryTest(unittest.TestCase):

    def getDataset(self):
        raise unittest.SkipTest('getDataset must be implemented')

    def setUp(self):
        self.dset = self.getDataset()
        self.wrapper = FORMDataset(self.dset)  # noqa: F405

    def test_get_dataset(self):
        array = self.wrapper.get_dataset()
        self.assertIsInstance(array, SortedArray)  # noqa: F405

    def test___gt__(self):
        '''
        Test wrapper greater than magic method
        '''
        q = self.wrapper > 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    False, True, True, True, True]
        expected = slice(6, 10)
        self.assertEqual(result, expected)

    def test___ge__(self):
        '''
        Test wrapper greater than or equal magic method
        '''
        q = self.wrapper >= 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    True, True, True, True, True]
        expected = slice(5, 10)
        self.assertEqual(result, expected)

    def test___lt__(self):
        '''
        Test wrapper less than magic method
        '''
        q = self.wrapper < 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    False, False, False, False, False]
        expected = slice(0, 5)
        self.assertEqual(result, expected)

    def test___le__(self):
        '''
        Test wrapper less than or equal magic method
        '''
        q = self.wrapper <= 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    True, False, False, False, False]
        expected = slice(0, 6)
        self.assertEqual(result, expected)

    def test___eq__(self):
        '''
        Test wrapper equals magic method
        '''
        q = self.wrapper == 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    True, False, False, False, False]
        expected = 5
        self.assertTrue(np.array_equal(result, expected))

    def test___ne__(self):
        '''
        Test wrapper not equal magic method
        '''
        q = self.wrapper != 5
        self.assertIsInstance(q, Query)  # noqa: F405
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    False, True, True, True, True]
        expected = [slice(0, 5), slice(6, 10)]
        self.assertTrue(np.array_equal(result, expected))

    def test___getitem__(self):
        '''
        Test wrapper getitem using slice
        '''
        result = self.wrapper[0:5]
        expected = [0, 1, 2, 3, 4]
        self.assertTrue(np.array_equal(result, expected))

    def test___getitem__query(self):
        '''
        Test wrapper getitem using query
        '''
        q = self.wrapper < 5
        result = self.wrapper[q]
        expected = [0, 1, 2, 3, 4]
        self.assertTrue(np.array_equal(result, expected))


class SortedQueryTest(AbstractQueryTest):

    path = 'SortedQueryTest.h5'

    def getDataset(self):
        self.f = File(self.path, 'w')
        self.input = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.d = self.f.create_dataset('dset', data=self.input)
        return SortedArray(self.d)  # noqa: F405

    def tearDown(self):
        self.f.close()
        if os.path.exists(self.path):
            os.remove(self.path)


class LinspaceQueryTest(AbstractQueryTest):

    path = 'LinspaceQueryTest.h5'

    def getDataset(self):
        return LinSpace(0, 10, 1)  # noqa: F405
