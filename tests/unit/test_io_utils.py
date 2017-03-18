import unittest

from pynwb.io.utils import DataChunkIterator
import numpy as np


class DataChunkIteratorTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_none_iter(self):
        dci = DataChunkIterator(None)
        self.assertIsNone(dci.max_shape)
        self.assertIsNone(dci.dtype)
        count = 0
        for v, l in dci:
            self.assertEqual(v, None)
            self.assertEqual(l, None)
            count+=1
        self.assertEqual(count, 0)
        self.assertIsNone(dci.recommended_data_shape(), None)
        self.assertIsNone(dci.recommended_chunk_shape(), None)

    def test_numpy_iter_unbuffered(self):
        a = np.arange(20).reshape(10,2)
        dci = DataChunkIterator(data=a, buffer_size=1)
        count = 0
        for v, l in dci:
            self.assertEqual(v.shape[0], 1)
            self.assertEqual(v.shape[1], 2)
            count+=1
        self.assertEqual(count, 10)
        self.assertTupleEqual(dci.recommended_data_shape(), a.shape)
        self.assertTupleEqual(dci.recommended_chunk_shape(), (1,2))

    def test_numpy_iter_unmatched_buffer_size(self):
        a = np.arange(10)
        dci = DataChunkIterator(data=a, buffer_size=3)
        self.assertTupleEqual(dci.max_shape, a.shape)
        self.assertEquals(dci.dtype, a.dtype)
        count = 0
        for v, l in dci:
            if count < 3:
                self.assertEqual(v.shape[0], 3)
            else:
                self.assertEqual(v.shape[0], 1)
            count +=1
        self.assertEqual(count, 4)
        self.assertTupleEqual(dci.recommended_data_shape(), a.shape)
        self.assertTupleEqual(dci.recommended_chunk_shape(), (3,))

    def test_standard_iterator_unbuffered(self):
        dci = DataChunkIterator(data=range(10), buffer_size=1)
        self.assertEquals(dci.dtype, np.dtype(int))
        self.assertTupleEqual(dci.max_shape, (None,))
        count = 0
        for v, l in dci:
            self.assertEqual(v.shape[0], 1)
            count+=1
        self.assertEqual(count, 10)
        self.assertTupleEqual(dci.recommended_data_shape(), (1,))
        self.assertTupleEqual(dci.recommended_chunk_shape(), (1,))

    def test_standard_iterator_unmatched_buffersized(self):
        dci = DataChunkIterator(data=range(10), buffer_size=3)
        self.assertEquals(dci.dtype, np.dtype(int))
        self.assertTupleEqual(dci.max_shape, (None,))
        count = 0
        for v, l in dci:
            if count < 3:
                self.assertEqual(v.shape[0], 3)
            else:
                self.assertEqual(v.shape[0], 1)
            count +=1
        self.assertEqual(count, 4)
        self.assertTupleEqual(dci.recommended_data_shape(), (3,))
        self.assertTupleEqual(dci.recommended_chunk_shape(), (3,))

    def test_multidimensional_list(self):
        a = np.arange(30).reshape(5,2,3).tolist()
        dci = DataChunkIterator(a)
        self.assertTupleEqual(dci.max_shape, (5,2,3))
        self.assertEqual(dci.dtype, np.dtype(int))
        count = 0
        for v, l in dci:
            self.assertTupleEqual(v.shape, (1,2,3))
            count +=1
        self.assertEquals(count, 5)
        self.assertTupleEqual(dci.recommended_data_shape(), (5, 2, 3))
        self.assertTupleEqual(dci.recommended_chunk_shape(), (1, 2, 3))


if __name__ == '__main__':
    unittest.main()

