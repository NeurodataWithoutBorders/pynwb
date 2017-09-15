import unittest

from form.data_utils import DataChunkIterator
from form.backends.hdf5.h5tools import __chunked_iter_fill__, write_dataset

import h5py
import tempfile
import numpy as np

class H5IOTest(unittest.TestCase):
    """Tests for h5tools IO tools"""


    def setUp(self):
        self.test_temp_file = tempfile.NamedTemporaryFile()
        self.f = h5py.File(self.test_temp_file.name, 'w')

    def tearDown(self):
        del self.f
        del self.test_temp_file
        self.f = None
        self.test_temp_file = None

    ##########################################
    #  __chunked_iter_fill__(...) tests
    ##########################################
    def test__chunked_iter_fill_iterator_matched_buffer_size(self):
        dci = DataChunkIterator(data=range(10), buffer_size=2)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertListEqual(my_dset[:].tolist(), list(range(10)))

    def test__chunked_iter_fill_iterator_unmatched_buffer_size(self):
        dci = DataChunkIterator(data=range(10), buffer_size=3)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertListEqual(my_dset[:].tolist(), list(range(10)))

    def test__chunked_iter_fill_numpy_matched_buffer_size(self):
        a = np.arange(30).reshape(5,2,3)
        dci = DataChunkIterator(data=a, buffer_size=1)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_numpy_unmatched_buffer_size(self):
        a = np.arange(30).reshape(5,2,3)
        dci = DataChunkIterator(data=a, buffer_size=3)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_list_matched_buffer_size(self):
        a = np.arange(30).reshape(5,2,3)
        dci = DataChunkIterator(data=a.tolist(), buffer_size=1)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_numpy_unmatched_buffer_size(self):
        a = np.arange(30).reshape(5,2,3)
        dci = DataChunkIterator(data=a.tolist(), buffer_size=3)
        my_dset = __chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    ##########################################
    #  write_dataset tests
    ##########################################
    def test_write_dataset_scalar(self):
        a = 10
        write_dataset(self.f, 'test_dataset', a, {})
        dset = self.f['test_dataset']
        self.assertTupleEqual(dset.shape, ())
        self.assertEqual(dset[()], a)

    def test_write_dataset_string(self):
        a = 'test string'
        write_dataset(self.f, 'test_dataset', a, {})
        dset = self.f['test_dataset']
        self.assertTupleEqual(dset.shape, ())
        #self.assertEqual(dset[()].decode('utf-8'), a)
        self.assertEqual(dset[()], a)

    def test_write_dataset_list(self):
        a = np.arange(30).reshape(5,2,3)
        write_dataset(self.f, 'test_dataset', a.tolist(), {})
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a))

    def test_write_table(self):
        cmpd_dt = np.dtype([('a', int), ('b', float)])
        data = np.zeros(10, dtype=cmpd_dt)
        data['a'][1] = 101
        data['b'][1] = 10.1
        dt = [{'name': 'a', 'dtype': 'int'  , 'doc': 'a column'},
              {'name': 'b', 'dtype': 'float', 'doc': 'b column'}]
        write_dataset(self.f, 'test_dataset', data, {}, dtype=dt)
        dset = self.f['test_dataset']
        self.assertEqual(dset['a'].tolist(), data['a'].tolist())
        self.assertEqual(dset['b'].tolist(), data['b'].tolist())

    def test_write_table_nested(self):
        b_cmpd_dt = np.dtype([('c', int), ('d', float)])
        cmpd_dt = np.dtype([('a', int), ('b', b_cmpd_dt)])
        data = np.zeros(10, dtype=cmpd_dt)
        data['a'][1] = 101
        data['b']['c'] = 202
        data['b']['d'] = 10.1
        b_dt = [{'name': 'c', 'dtype': 'int'  , 'doc': 'c column'},
                {'name': 'd', 'dtype': 'float', 'doc': 'd column'}]
        dt = [{'name': 'a', 'dtype': 'int', 'doc': 'a column'},
              {'name': 'b', 'dtype': b_dt , 'doc': 'b column'}]
        write_dataset(self.f, 'test_dataset', data, {}, dtype=dt)
        dset = self.f['test_dataset']
        self.assertEqual(dset['a'].tolist(), data['a'].tolist())
        self.assertEqual(dset['b'].tolist(), data['b'].tolist())

    def test_write_dataset_iterable(self):
        write_dataset(self.f, 'test_dataset', range(10), {})
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), list(range(10)))

    def test_write_dataset_iterable_multidimensional_array(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        write_dataset(self.f, 'test_dataset', aiter, {})
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), a.tolist())

    def test_write_dataset_data_chunk_iterator(self):
        dci = DataChunkIterator(data=np.arange(10), buffer_size=2)
        write_dataset(self.f, 'test_dataset', dci, {})
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), list(range(10)))


if __name__ == '__main__':
    unittest.main()

