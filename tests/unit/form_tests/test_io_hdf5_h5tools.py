import os
import unittest

from pynwb.form.data_utils import DataChunkIterator
from pynwb.form.backends.hdf5.h5tools import HDF5IO
from pynwb.form.backends.hdf5 import H5DataIO
from pynwb.form.build import DatasetBuilder
from h5py import SoftLink, HardLink

import tempfile
import warnings
import numpy as np


class H5IOTest(unittest.TestCase):
    """Tests for h5tools IO tools"""

    def setUp(self):
        self.test_temp_file = tempfile.NamedTemporaryFile()

        # On Windows h5py cannot truncate an open file in write mode.
        # The temp file will be closed before h5py truncates it
        # and will be removed during the tearDown step.
        self.test_temp_file.close()
        self.io = HDF5IO(self.test_temp_file.name)
        self.f = self.io._file

    def tearDown(self):
        path = self.f.filename
        self.f.close()
        os.remove(path)
        del self.f
        del self.test_temp_file
        self.f = None
        self.test_temp_file = None

    ##########################################
    #  __chunked_iter_fill__(...) tests
    ##########################################
    def test__chunked_iter_fill_iterator_matched_buffer_size(self):
        dci = DataChunkIterator(data=range(10), buffer_size=2)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertListEqual(my_dset[:].tolist(), list(range(10)))

    def test__chunked_iter_fill_iterator_unmatched_buffer_size(self):
        dci = DataChunkIterator(data=range(10), buffer_size=3)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertListEqual(my_dset[:].tolist(), list(range(10)))

    def test__chunked_iter_fill_numpy_matched_buffer_size(self):
        a = np.arange(30).reshape(5, 2, 3)
        dci = DataChunkIterator(data=a, buffer_size=1)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_numpy_unmatched_buffer_size(self):
        a = np.arange(30).reshape(5, 2, 3)
        dci = DataChunkIterator(data=a, buffer_size=3)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_list_matched_buffer_size(self):
        a = np.arange(30).reshape(5, 2, 3)
        dci = DataChunkIterator(data=a.tolist(), buffer_size=1)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    def test__chunked_iter_fill_numpy_unmatched_buffer_size(self):  # noqa: F811
        a = np.arange(30).reshape(5, 2, 3)
        dci = DataChunkIterator(data=a.tolist(), buffer_size=3)
        my_dset = HDF5IO.__chunked_iter_fill__(self.f, 'test_dataset', dci)
        self.assertTrue(np.all(my_dset[:] == a))
        self.assertTupleEqual(my_dset.shape, a.shape)

    ##########################################
    #  write_dataset tests: scalars
    ##########################################
    def test_write_dataset_scalar(self):
        a = 10
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTupleEqual(dset.shape, ())
        self.assertEqual(dset[()], a)

    def test_write_dataset_string(self):
        a = 'test string'
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTupleEqual(dset.shape, ())
        # self.assertEqual(dset[()].decode('utf-8'), a)
        self.assertEqual(dset[()], a)

    ##########################################
    #  write_dataset tests: lists
    ##########################################
    def test_write_dataset_list(self):
        a = np.arange(30).reshape(5, 2, 3)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a.tolist(), attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a))

    def test_write_dataset_list_compress(self):
        a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                     compression='gzip',
                     compression_opts=5,
                     shuffle=True,
                     fletcher32=True)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a.data))
        self.assertEqual(dset.compression, 'gzip')
        self.assertEqual(dset.compression_opts, 5)
        self.assertEqual(dset.shuffle, True)
        self.assertEqual(dset.fletcher32, True)

    def test_write_dataset_list_chunked(self):
        a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                     chunks=(1, 1, 3))
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a.data))
        self.assertEqual(dset.chunks, (1, 1, 3))

    def test_write_dataset_list_fillvalue(self):
        a = H5DataIO(np.arange(20).reshape(5, 4), fillvalue=-1)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a.data))
        self.assertEqual(dset.fillvalue, -1)

    ##########################################
    #  write_dataset tests: tables
    ##########################################
    def test_write_table(self):
        cmpd_dt = np.dtype([('a', np.int32), ('b', np.float64)])
        data = np.zeros(10, dtype=cmpd_dt)
        data['a'][1] = 101
        data['b'][1] = 0.1
        dt = [{'name': 'a', 'dtype': 'int32', 'doc': 'a column'},
              {'name': 'b', 'dtype': 'float64', 'doc': 'b column'}]
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', data, attributes={}, dtype=dt))
        dset = self.f['test_dataset']
        self.assertEqual(dset['a'].tolist(), data['a'].tolist())
        self.assertEqual(dset['b'].tolist(), data['b'].tolist())

    def test_write_table_nested(self):
        b_cmpd_dt = np.dtype([('c', np.int32), ('d', np.float64)])
        cmpd_dt = np.dtype([('a', np.int32), ('b', b_cmpd_dt)])
        data = np.zeros(10, dtype=cmpd_dt)
        data['a'][1] = 101
        data['b']['c'] = 202
        data['b']['d'] = 10.1
        b_dt = [{'name': 'c', 'dtype': 'int32', 'doc': 'c column'},
                {'name': 'd', 'dtype': 'float64', 'doc': 'd column'}]
        dt = [{'name': 'a', 'dtype': 'int32', 'doc': 'a column'},
              {'name': 'b', 'dtype': b_dt, 'doc': 'b column'}]
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', data, attributes={}, dtype=dt))
        dset = self.f['test_dataset']
        self.assertEqual(dset['a'].tolist(), data['a'].tolist())
        self.assertEqual(dset['b'].tolist(), data['b'].tolist())

    ##########################################
    #  write_dataset tests: Iterable
    ##########################################
    def test_write_dataset_iterable(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', range(10), attributes={}))
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), list(range(10)))

    def test_write_dataset_iterable_multidimensional_array(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', daiter, attributes={}))
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), a.tolist())

    def test_write_dataset_iterable_multidimensional_array_compression(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        wrapped_daiter = H5DataIO(data=daiter,
                                  compression='gzip',
                                  compression_opts=5,
                                  shuffle=True,
                                  fletcher32=True)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', wrapped_daiter, attributes={}))
        dset = self.f['test_dataset']
        self.assertEqual(dset.shape, a.shape)
        self.assertListEqual(dset[:].tolist(), a.tolist())
        self.assertEqual(dset.compression, 'gzip')
        self.assertEqual(dset.compression_opts, 5)
        self.assertEqual(dset.shuffle, True)
        self.assertEqual(dset.fletcher32, True)

    #############################################
    #  write_dataset tests: data chunk iterator
    #############################################
    def test_write_dataset_data_chunk_iterator(self):
        dci = DataChunkIterator(data=np.arange(10), buffer_size=2)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', dci, attributes={}))
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), list(range(10)))

    def test_write_dataset_data_chunk_iterator_with_compression(self):
        dci = DataChunkIterator(data=np.arange(10), buffer_size=2)
        wrapped_dci = H5DataIO(data=dci,
                               compression='gzip',
                               compression_opts=5,
                               shuffle=True,
                               fletcher32=True,
                               chunks=(2,))
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', wrapped_dci, attributes={}))
        dset = self.f['test_dataset']
        self.assertListEqual(dset[:].tolist(), list(range(10)))
        self.assertEqual(dset.compression, 'gzip')
        self.assertEqual(dset.compression_opts, 5)
        self.assertEqual(dset.shuffle, True)
        self.assertEqual(dset.fletcher32, True)
        self.assertEqual(dset.chunks, (2,))

    def test_pass_through_of_recommended_chunks(self):

        class DC(DataChunkIterator):
            def recommended_chunk_shape(self):
                return (5, 1, 1)
        dci = DC(data=np.arange(30).reshape(5, 2, 3))
        wrapped_dci = H5DataIO(data=dci,
                               compression='gzip',
                               compression_opts=5,
                               shuffle=True,
                               fletcher32=True)
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', wrapped_dci, attributes={}))
        dset = self.f['test_dataset']
        self.assertEqual(dset.chunks, (5, 1, 1))
        self.assertEqual(dset.compression, 'gzip')
        self.assertEqual(dset.compression_opts, 5)
        self.assertEqual(dset.shuffle, True)
        self.assertEqual(dset.fletcher32, True)

    #############################################
    #  H5DataIO general
    #############################################
    def test_warning_on_non_gzip_compression(self):
        # Make sure no warning is issued when using gzip
        with warnings.catch_warnings(record=True) as w:
            dset = H5DataIO(np.arange(30),
                            compression='gzip')
            self.assertEqual(len(w), 0)
            self.assertEqual(dset.io_settings['compression'], 'gzip')
        # Make sure no warning is issued when using szip
        with warnings.catch_warnings(record=True) as w:
            dset = H5DataIO(np.arange(30),
                            compression='szip')
            self.assertEqual(len(w), 1)
            self.assertEqual(dset.io_settings['compression'], 'szip')
        # Make sure no warning is issued when using lzf
        with warnings.catch_warnings(record=True) as w:
            dset = H5DataIO(np.arange(30),
                            compression='lzf')
            self.assertEqual(len(w), 1)
            self.assertEqual(dset.io_settings['compression'], 'lzf')

    def test_warning_on_linking_of_regular_array(self):
        with warnings.catch_warnings(record=True) as w:
            dset = H5DataIO(np.arange(30),
                            link_data=True)
            self.assertEqual(len(w), 1)
            self.assertEqual(dset.link_data, False)

    def test_warning_on_setting_io_options_on_h5dataset_input(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', np.arange(10), attributes={}))
        with warnings.catch_warnings(record=True) as w:
            H5DataIO(self.f['test_dataset'],
                     compression='gzip',
                     compression_opts=4,
                     fletcher32=True,
                     shuffle=True,
                     maxshape=(10, 20),
                     chunks=(10,),
                     fillvalue=100)
            self.assertEqual(len(w), 7)

    #############################################
    #  Copy/Link h5py.Dataset object
    #############################################
    def test_link_h5py_dataset_input(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', np.arange(10), attributes={}))
        self.io.write_dataset(self.f, DatasetBuilder('test_softlink', self.f['test_dataset'], attributes={}))
        self.assertTrue(isinstance(self.f.get('test_softlink', getlink=True), SoftLink))

    def test_copy_h5py_dataset_input(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', np.arange(10), attributes={}))
        self.io.write_dataset(self.f,
                              DatasetBuilder('test_copy', self.f['test_dataset'], attributes={}),
                              link_data=False)
        self.assertTrue(isinstance(self.f.get('test_copy', getlink=True), HardLink))
        self.assertListEqual(self.f['test_dataset'][:].tolist(),
                             self.f['test_copy'][:].tolist())

    def test_link_h5py_dataset_h5dataio_input(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', np.arange(10), attributes={}))
        self.io.write_dataset(self.f, DatasetBuilder('test_softlink',
                                                     H5DataIO(data=self.f['test_dataset'],
                                                              link_data=True),
                                                     attributes={}))
        self.assertTrue(isinstance(self.f.get('test_softlink', getlink=True), SoftLink))

    def test_copy_h5py_dataset_h5dataio_input(self):
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', np.arange(10), attributes={}))
        self.io.write_dataset(self.f,
                              DatasetBuilder('test_copy',
                                             H5DataIO(data=self.f['test_dataset'],
                                                      link_data=False),  # Force dataset copy
                                             attributes={}),
                              link_data=True)  # Make sure the default behavior is set to link the data
        self.assertTrue(isinstance(self.f.get('test_copy', getlink=True), HardLink))
        self.assertListEqual(self.f['test_dataset'][:].tolist(),
                             self.f['test_copy'][:].tolist())


if __name__ == '__main__':
    unittest.main()
