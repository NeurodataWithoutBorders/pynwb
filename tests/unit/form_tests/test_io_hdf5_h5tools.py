import os
import unittest

from pynwb.form.data_utils import DataChunkIterator
from pynwb.form.backends.hdf5.h5tools import HDF5IO
from pynwb.form.backends.hdf5 import H5DataIO
from pynwb.form.build import DatasetBuilder
from pynwb.form.spec.namespace import NamespaceCatalog
from h5py import SoftLink, HardLink, ExternalLink, File
from pynwb.file import NWBFile
from pynwb.base import TimeSeries
from pynwb import NWBHDF5IO
from pynwb.spec import NWBNamespace, NWBGroupSpec, NWBDatasetSpec

from pynwb.ecephys import ElectricalSeries


import tempfile
import warnings
import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal


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

    def test_write_dataset_list_enable_default_compress(self):
        a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                     compression=True)
        self.assertEqual(a.io_settings['compression'], 'gzip')
        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a.data))
        self.assertEqual(dset.compression, 'gzip')

    def test_write_dataset_list_disable_default_compress(self):
        with warnings.catch_warnings(record=True) as w:
            a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                         compression=False,
                         compression_opts=5)
            self.assertEqual(len(w), 1)  # We expect a warning that compression options are being ignored
            self.assertFalse('compression_ops' in a.io_settings)
            self.assertFalse('compression' in a.io_settings)

        self.io.write_dataset(self.f, DatasetBuilder('test_dataset', a, attributes={}))
        dset = self.f['test_dataset']
        self.assertTrue(np.all(dset[:] == a.data))
        self.assertEqual(dset.compression, None)

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


class TestCacheSpec(unittest.TestCase):

    def test_cache_spec(self):
        self.test_temp_file = tempfile.NamedTemporaryFile()
        # On Windows h5py cannot truncate an open file in write mode.
        # The temp file will be closed before h5py truncates it
        # and will be removed during the tearDown step.
        self.test_temp_file.close()
        self.io = NWBHDF5IO(self.test_temp_file.name)
        # Setup all the data we need
        start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
        create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        data = np.arange(1000).reshape((100, 10))
        timestamps = np.arange(100)
        # Create the first file
        nwbfile1 = NWBFile(session_description='demonstrate external files',
                           identifier='NWBE1',
                           session_start_time=start_time,
                           file_create_date=create_date)

        test_ts1 = TimeSeries(name='test_timeseries',
                              data=data,
                              unit='SIunit',
                              timestamps=timestamps)
        nwbfile1.add_acquisition(test_ts1)
        # Write the first file
        self.io.write(nwbfile1, cache_spec=True)
        self.io.close()
        ns_catalog = NamespaceCatalog(group_spec_cls=NWBGroupSpec,
                                      dataset_spec_cls=NWBDatasetSpec,
                                      spec_namespace_cls=NWBNamespace)
        NWBHDF5IO.load_namespaces(ns_catalog, self.test_temp_file.name)
        self.assertEqual(ns_catalog.namespaces, ('core',))
        source_types = self.__get_types(self.io.manager.namespace_catalog)
        read_types = self.__get_types(ns_catalog)
        self.assertSetEqual(source_types, read_types)

    def __get_types(self, catalog):
        types = set()
        for ns_name in catalog.namespaces:
            ns = catalog.get_namespace(ns_name)
            for source in ns['schema']:
                types.update(catalog.get_types(source['source']))
        return types


class TestLinkResolution(unittest.TestCase):

    def test_link_resolve(self):
        nwbfile = NWBFile("a file with header data", "NB123A", datetime(2018, 6, 1, tzinfo=tzlocal()))
        device = nwbfile.create_device('device_name')
        electrode_group = nwbfile.create_electrode_group(
            name='electrode_group_name',
            description='desc',
            device=device,
            location='unknown')
        nwbfile.add_electrode(id=0,
                              x=1.0, y=2.0, z=3.0,  # position?
                              imp=2.718,
                              location='unknown',
                              filtering='unknown',
                              group=electrode_group)
        etr = nwbfile.create_electrode_table_region([0], 'etr_name')
        for passband in ('theta', 'gamma'):
            electrical_series = ElectricalSeries(name=passband + '_phase',
                                                 data=[1., 2., 3.],
                                                 rate=0.0,
                                                 electrodes=etr)
            nwbfile.add_acquisition(electrical_series)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(self.path, 'r') as io:
            io.read()

    def setUp(self):
        self.path = "test_link_resolve.nwb"

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)


class NWBHDF5IOMultiFileTest(unittest.TestCase):
    """Tests for h5tools IO tools"""

    def setUp(self):
        numfiles = 3
        self.test_temp_files = [tempfile.NamedTemporaryFile() for i in range(numfiles)]

        # On Windows h5py cannot truncate an open file in write mode.
        # The temp file will be closed before h5py truncates it
        # and will be removed during the tearDown step.
        for i in self.test_temp_files:
            i.close()
        self.io = [NWBHDF5IO(i.name) for i in self.test_temp_files]
        self.f = [i._file for i in self.io]

    def tearDown(self):
        # Close all the files
        for i in self.io:
            i.close()
            del(i)
        self.io = None
        self.f = None
        # Make sure the files have been deleted
        for tf in self.test_temp_files:
            try:
                os.remove(tf.name)
            except OSError:
                pass
        self.test_temp_files = None

    def test_copy_file_with_external_links(self):
        # Setup all the data we need
        start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
        create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        data = np.arange(1000).reshape((100, 10))
        timestamps = np.arange(100)
        # Create the first file
        nwbfile1 = NWBFile(session_description='demonstrate external files',
                           identifier='NWBE1',
                           session_start_time=start_time,
                           file_create_date=create_date)

        test_ts1 = TimeSeries(name='test_timeseries',
                              data=data,
                              unit='SIunit',
                              timestamps=timestamps)
        nwbfile1.add_acquisition(test_ts1)
        # Write the first file
        self.io[0].write(nwbfile1)
        nwbfile1_read = self.io[0].read()

        # Create the second file
        nwbfile2 = NWBFile(session_description='demonstrate external files',
                           identifier='NWBE1',
                           session_start_time=start_time,
                           file_create_date=create_date)

        test_ts2 = TimeSeries(name='test_timeseries',
                              data=nwbfile1_read.get_acquisition('test_timeseries').data,
                              unit='SIunit',
                              timestamps=timestamps)
        nwbfile2.add_acquisition(test_ts2)
        # Write the second file
        self.io[1].write(nwbfile2)
        self.io[1].close()
        self.io[0].close()  # Don't forget to close the first file too

        # Copy the file
        self.io[2].close()
        HDF5IO.copy_file(source_filename=self.test_temp_files[1].name,
                         dest_filename=self.test_temp_files[2].name,
                         expand_external=True,
                         expand_soft=False,
                         expand_refs=False)

        # Test that everything is working as expected
        # Confirm that our original data file is correct
        f1 = File(self.test_temp_files[0].name)
        self.assertTrue(isinstance(f1.get('/acquisition/test_timeseries/data', getlink=True), HardLink))
        # Confirm that we successfully created and External Link in our second file
        f2 = File(self.test_temp_files[1].name)
        self.assertTrue(isinstance(f2.get('/acquisition/test_timeseries/data', getlink=True), ExternalLink))
        # Confirm that we successfully resolved the External Link when we copied our second file
        f3 = File(self.test_temp_files[2].name)
        self.assertTrue(isinstance(f3.get('/acquisition/test_timeseries/data', getlink=True), HardLink))


if __name__ == '__main__':
    unittest.main()
