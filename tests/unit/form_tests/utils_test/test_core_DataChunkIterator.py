import unittest2 as unittest

from pynwb.form.data_utils import DataChunkIterator, DataChunk
import numpy as np


class DataChunkIteratorTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_none_iter(self):
        dci = DataChunkIterator(None)
        self.assertIsNone(dci.maxshape)
        self.assertIsNone(dci.dtype)
        count = 0
        for chunk in dci:
            self.assertEqual(chunk.data, None)
            self.assertEqual(chunk.selection, None)
            count += 1
        self.assertEqual(count, 0)
        self.assertIsNone(dci.recommended_data_shape())
        self.assertIsNone(dci.recommended_chunk_shape())

    """ def test_numpy_iter_unbuffered(self):
        a = np.arange(20).reshape(10,2)
        dci = DataChunkIterator(data=a, buffer_size=1)
        count = 0
        for v, l in dci:
            self.assertEqual(v.shape[0], 1)
            self.assertEqual(v.shape[1], 2)
            count+=1
        self.assertEqual(count, 10)
        self.assertTupleEqual(dci.recommended_data_shape(), a.shape)
        self.assertIsNone(dci.recommended_chunk_shape())"""

    def test_numpy_iter_unmatched_buffer_size(self):
        a = np.arange(10)
        dci = DataChunkIterator(data=a, buffer_size=3)
        self.assertTupleEqual(dci.maxshape, a.shape)
        self.assertEquals(dci.dtype, a.dtype)
        count = 0
        for chunk in dci:
            if count < 3:
                self.assertEqual(chunk.data.shape[0], 3)
            else:
                self.assertEqual(chunk.data.shape[0], 1)
            count += 1
        self.assertEqual(count, 4)
        self.assertTupleEqual(dci.recommended_data_shape(), a.shape)
        self.assertIsNone(dci.recommended_chunk_shape())

    def test_standard_iterator_unbuffered(self):
        dci = DataChunkIterator(data=range(10), buffer_size=1)
        self.assertEqual(dci.dtype, np.dtype(int))
        self.assertTupleEqual(dci.maxshape, (10,))
        self.assertTupleEqual(dci.recommended_data_shape(), (10,))  # Test before and after iteration
        count = 0
        for chunk in dci:
            self.assertEqual(chunk.data.shape[0], 1)
            count += 1
        self.assertEqual(count, 10)
        self.assertTupleEqual(dci.recommended_data_shape(), (10,))  # Test before and after iteration
        self.assertIsNone(dci.recommended_chunk_shape())

    def test_standard_iterator_unmatched_buffersized(self):
        dci = DataChunkIterator(data=range(10), buffer_size=3)
        self.assertEquals(dci.dtype, np.dtype(int))
        self.assertTupleEqual(dci.maxshape, (10,))
        self.assertIsNone(dci.recommended_chunk_shape())
        self.assertTupleEqual(dci.recommended_data_shape(), (10,))  # Test before and after iteration
        count = 0
        for chunk in dci:
            if count < 3:
                self.assertEqual(chunk.data.shape[0], 3)
            else:
                self.assertEqual(chunk.data.shape[0], 1)
            count += 1
        self.assertTupleEqual(dci.recommended_data_shape(), (10,))  # Test before and after iteration
        self.assertEqual(count, 4)

    def test_multidimensional_list(self):
        a = np.arange(30).reshape(5, 2, 3).tolist()
        dci = DataChunkIterator(a)
        self.assertTupleEqual(dci.maxshape, (5, 2, 3))
        self.assertEqual(dci.dtype, np.dtype(int))
        count = 0
        for chunk in dci:
            self.assertTupleEqual(chunk.data.shape, (1, 2, 3))
            count += 1
        self.assertEquals(count, 5)
        self.assertTupleEqual(dci.recommended_data_shape(), (5, 2, 3))
        self.assertIsNone(dci.recommended_chunk_shape())

    def test_maxshape(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        self.assertEqual(daiter.maxshape, (None, 2, 3))

    def test_dtype(self):
        a = np.arange(30, dtype='int32').reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        self.assertEqual(daiter.dtype, a.dtype)


class DataChunkTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_len_operator_no_data(self):
        temp = DataChunk()
        self.assertEqual(len(temp), 0)

    def test_len_operator_with_data(self):
        temp = DataChunk(np.arange(10).reshape(5, 2))
        self.assertEqual(len(temp), 5)


if __name__ == '__main__':
    unittest.main()
