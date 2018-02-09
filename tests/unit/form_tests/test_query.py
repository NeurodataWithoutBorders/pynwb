import unittest
import os
from h5py import File
import numpy as np

from pynwb.form.query import Query, H5Dataset


class QueryTest(unittest.TestCase):

    path = 'QueryTest.h5'

    def setUp(self):
        self.f = File(self.path, 'w')
        self.input = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.d = self.f.create_dataset('dset', data=self.input)
        # self.f = File(self.path, 'r')
        # self.d = self.f['dset']
        self.wrapper = H5Dataset(self.d)

    def tearDown(self):
        self.f.close()
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_get_array(self):
        array = self.wrapper.get_array()
        self.assertIsInstance(array, np.ndarray)
        self.assertTrue(np.array_equal(array, self.d))

    def test___gt__(self):
        q = self.wrapper > 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    False, True, True, True, True]
        self.assertTrue(np.array_equal(result, expected))

    def test___ge__(self):
        q = self.wrapper >= 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    True, True, True, True, True]
        self.assertTrue(np.array_equal(result, expected))

    def test___lt__(self):
        q = self.wrapper < 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    False, False, False, False, False]
        self.assertTrue(np.array_equal(result, expected))

    def test___le__(self):
        q = self.wrapper <= 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    True, False, False, False, False]
        self.assertTrue(np.array_equal(result, expected))

    def test___eq__(self):
        q = self.wrapper == 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [False, False, False, False, False,
                    True, False, False, False, False]
        self.assertTrue(np.array_equal(result, expected))

    def test___ne__(self):
        q = self.wrapper != 5
        self.assertIsInstance(q, Query)
        result = q.evaluate()
        expected = [True, True, True, True, True,
                    False, True, True, True, True]
        self.assertTrue(np.array_equal(result, expected))

    def test___getitem__query(self):
        q = self.wrapper < 5
        result = self.wrapper[q]
        expected = [0, 1, 2, 3, 4]
        self.assertTrue(np.array_equal(result, expected))
