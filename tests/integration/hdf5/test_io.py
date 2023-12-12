from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import numpy as np
from h5py import File
from pathlib import Path
import tempfile

from pynwb import NWBFile, TimeSeries, get_manager, NWBHDF5IO, validate

from hdmf.backends.io import UnsupportedOperation
from hdmf.backends.hdf5 import HDF5IO, H5DataIO
from hdmf.data_utils import DataChunkIterator
from hdmf.build import GroupBuilder, DatasetBuilder
from hdmf.spec import NamespaceCatalog
from pynwb.spec import NWBGroupSpec, NWBDatasetSpec, NWBNamespace
from pynwb.ecephys import ElectricalSeries, LFP
from pynwb.testing import remove_test_file, TestCase
from pynwb.testing.mock.file import mock_NWBFile


class TestHDF5Writer(TestCase):

    _required_tests = ('test_nwbio', 'test_write_clobber', 'test_write_cache_spec', 'test_write_no_cache_spec')

    @property
    def required_tests(self):
        return self._required_tests

    def setUp(self):
        self.manager = get_manager()
        self.path = "test_pynwb_io_hdf5.nwb"
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        self.container = NWBFile(session_description='a test NWB File', identifier='TEST123',
                                 session_start_time=self.start_time, file_create_date=self.create_date)
        ts = TimeSeries(name='test_timeseries', data=list(range(100, 200, 10)), unit='SIunit',
                        timestamps=np.arange(10.), resolution=0.1)
        self.container.add_acquisition(ts)

        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'neurodata_type': 'TimeSeries'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder('timestamps', np.arange(10.),
                                                                         attributes={'unit': 'seconds',
                                                                                     'interval': 1})})
        self.builder = GroupBuilder(
            'root', groups={'acquisition': GroupBuilder('acquisition', groups={'test_timeseries': ts_builder}),
                            'analysis': GroupBuilder('analysis'),
                            'general': GroupBuilder('general'),
                            'processing': GroupBuilder('processing'),
                            'stimulus': GroupBuilder(
                                'stimulus',
                                groups={'presentation': GroupBuilder('presentation'),
                                        'templates': GroupBuilder('templates')})},
            datasets={'file_create_date': DatasetBuilder('file_create_date', [self.create_date.isoformat()]),
                      'identifier': DatasetBuilder('identifier', 'TEST123'),
                      'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                      'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                      'session_start_time': DatasetBuilder('session_start_time', self.start_time.isoformat())},
            attributes={'neurodata_type': 'NWBFile'})

    def tearDown(self):
        remove_test_file(self.path)

    def test_nwbio(self):
        with HDF5IO(self.path, manager=self.manager, mode='a') as io:
            io.write(self.container)
        with File(self.path, 'r') as f:
            self.assertIn('acquisition', f)
            self.assertIn('analysis', f)
            self.assertIn('general', f)
            self.assertIn('processing', f)
            self.assertIn('file_create_date', f)
            self.assertIn('identifier', f)
            self.assertIn('session_description', f)
            self.assertIn('session_start_time', f)
            acq = f.get('acquisition')
            self.assertIn('test_timeseries', acq)

    def test_write_clobber(self):
        with HDF5IO(self.path, manager=self.manager, mode='a') as io:
            io.write(self.container)

        with self.assertRaisesWith(UnsupportedOperation,
                                   "Unable to open file %s in 'w-' mode. File already exists." % self.path):
            with HDF5IO(self.path, manager=self.manager, mode='w-') as io:
                pass

    def test_write_cache_spec(self):
        '''
        Round-trip test for writing spec and reading it back in
        '''
        with HDF5IO(self.path, manager=self.manager, mode="a") as io:
            io.write(self.container)
        with File(self.path, 'r') as f:
            self.assertIn('specifications', f)

        ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
        HDF5IO.load_namespaces(ns_catalog, self.path)
        original_ns = self.manager.namespace_catalog.get_namespace('core')
        cached_ns = ns_catalog.get_namespace('core')
        self.maxDiff = None
        for key in ('author', 'contact', 'doc', 'full_name', 'name'):
            with self.subTest(namespace_field=key):
                self.assertEqual(original_ns[key], cached_ns[key])
        for dt in original_ns.get_registered_types():
            with self.subTest(neurodata_type=dt):
                original_spec = original_ns.get_spec(dt)
                cached_spec = cached_ns.get_spec(dt)
                with self.subTest(test='data_type spec read back in'):
                    self.assertIsNotNone(cached_spec)
                with self.subTest(test='cached spec preserved original spec'):
                    self.assertDictEqual(original_spec, cached_spec)

    def test_write_no_cache_spec(self):
        '''
        Round-trip test for not writing spec
        '''
        with HDF5IO(self.path, manager=self.manager, mode="a") as io:
            io.write(self.container, cache_spec=False)
        with File(self.path, 'r') as f:
            self.assertNotIn('specifications', f)

    def test_file_creation_io_modes(self):
        io_modes_that_create_file = ["w", "w-", "x"]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            for io_mode in io_modes_that_create_file:
                file_path = temp_dir / f"test_io_mode={io_mode}.nwb"

                # Test file creation
                nwbfile = mock_NWBFile()
                with NWBHDF5IO(str(file_path), io_mode) as io:
                    io.write(nwbfile)


class TestHDF5WriterWithInjectedFile(TestCase):

    _required_tests = ('test_nwbio', 'test_write_clobber', 'test_write_cache_spec')

    @property
    def required_tests(self):
        return self._required_tests

    def setUp(self):
        self.manager = get_manager()
        self.path = "test_pynwb_io_hdf5_injected.nwb"
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        self.container = NWBFile(session_description='a test NWB File', identifier='TEST123',
                                 session_start_time=self.start_time, file_create_date=self.create_date)
        ts = TimeSeries(name='test_timeseries', data=list(range(100, 200, 10)), unit='SIunit',
                        timestamps=np.arange(10.), resolution=0.1)
        self.container.add_acquisition(ts)

        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'neurodata_type': 'TimeSeries'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder('timestamps', np.arange(10.),
                                                                         attributes={'unit': 'seconds',
                                                                                     'interval': 1})})
        self.builder = GroupBuilder(
            'root', groups={'acquisition': GroupBuilder('acquisition', groups={'test_timeseries': ts_builder}),
                            'analysis': GroupBuilder('analysis'),
                            'general': GroupBuilder('general'),
                            'processing': GroupBuilder('processing'),
                            'stimulus': GroupBuilder(
                                'stimulus',
                                groups={'presentation': GroupBuilder('presentation'),
                                        'templates': GroupBuilder('templates')})},
            datasets={'file_create_date': DatasetBuilder('file_create_date', [self.create_date.isoformat()]),
                      'identifier': DatasetBuilder('identifier', 'TEST123'),
                      'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                      'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                      'session_start_time': DatasetBuilder('session_start_time', self.start_time.isoformat())},
            attributes={'neurodata_type': 'NWBFile'})

    def tearDown(self):
        remove_test_file(self.path)

    def test_nwbio(self):
        with File(self.path, 'w') as fil:
            with HDF5IO(self.path, manager=self.manager, file=fil, mode='a') as io:
                io.write(self.container)
        with File(self.path, 'r') as f:
            self.assertIn('acquisition', f)
            self.assertIn('analysis', f)
            self.assertIn('general', f)
            self.assertIn('processing', f)
            self.assertIn('file_create_date', f)
            self.assertIn('identifier', f)
            self.assertIn('session_description', f)
            self.assertIn('session_start_time', f)
            acq = f.get('acquisition')
            self.assertIn('test_timeseries', acq)

    def test_write_clobber(self):
        with File(self.path, 'w') as fil:
            with HDF5IO(self.path, manager=self.manager, file=fil, mode='a') as io:
                io.write(self.container)

        with self.assertRaisesWith(UnsupportedOperation,
                                   "Unable to open file %s in 'w-' mode. File already exists." % self.path):
            with HDF5IO(self.path, manager=self.manager, mode='w-') as io:
                pass

    def test_write_cache_spec(self):
        '''
        Round-trip test for writing spec and reading it back in
        '''

        with File(self.path, 'w') as fil:
            with HDF5IO(self.path, manager=self.manager, file=fil, mode='a') as io:
                io.write(self.container)
        with File(self.path, 'r') as f:
            self.assertIn('specifications', f)

        ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
        HDF5IO.load_namespaces(ns_catalog, self.path)
        original_ns = self.manager.namespace_catalog.get_namespace('core')
        cached_ns = ns_catalog.get_namespace('core')
        self.maxDiff = None
        for key in ('author', 'contact', 'doc', 'full_name', 'name'):
            with self.subTest(namespace_field=key):
                self.assertEqual(original_ns[key], cached_ns[key])
        for dt in original_ns.get_registered_types():
            with self.subTest(neurodata_type=dt):
                original_spec = original_ns.get_spec(dt)
                cached_spec = cached_ns.get_spec(dt)
                with self.subTest(test='data_type spec read back in'):
                    self.assertIsNotNone(cached_spec)
                with self.subTest(test='cached spec preserved original spec'):
                    self.assertDictEqual(original_spec, cached_spec)


class TestAppend(TestCase):

    def setUp(self):
        self.nwbfile = NWBFile(session_description='hi',
                               identifier='hi',
                               session_start_time=datetime(1970, 1, 1, 12, tzinfo=tzutc()))
        self.path = "test_append.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_append(self):
        proc_mod = self.nwbfile.create_processing_module(name='test_proc_mod', description='')
        proc_inter = LFP(name='LFP')
        proc_mod.add(proc_inter)
        device = self.nwbfile.create_device(name='test_device')
        e_group = self.nwbfile.create_electrode_group(
            name='test_electrode_group',
            description='',
            location='',
            device=device
        )
        self.nwbfile.add_electrode(x=0.0, y=0.0, z=0.0, imp=np.nan, location='loc', filtering='filt', group=e_group)
        electrodes = self.nwbfile.create_electrode_table_region(region=[0], description='')
        e_series = ElectricalSeries(
            name='test_es',
            electrodes=electrodes,
            data=np.ones(shape=(100,)),
            rate=10000.0,
        )
        proc_inter.add_electrical_series(e_series)

        with NWBHDF5IO(self.path, mode='w') as io:
            io.write(self.nwbfile, cache_spec=False)

        with NWBHDF5IO(self.path, mode='a') as io:
            nwb = io.read()
            link_electrodes = nwb.processing['test_proc_mod']['LFP'].electrical_series['test_es'].electrodes
            ts2 = ElectricalSeries(name='timeseries2', data=[4., 5., 6.], rate=1.0, electrodes=link_electrodes)
            nwb.add_acquisition(ts2)
            io.write(nwb)  # also attempt to write same spec again
            self.assertIs(nwb.processing['test_proc_mod']['LFP'].electrical_series['test_es'].electrodes,
                          nwb.acquisition['timeseries2'].electrodes)

        with NWBHDF5IO(self.path, mode='r') as io:
            nwb = io.read()
            np.testing.assert_equal(nwb.acquisition['timeseries2'].data[:], ts2.data)
            self.assertIs(nwb.processing['test_proc_mod']['LFP'].electrical_series['test_es'].electrodes,
                          nwb.acquisition['timeseries2'].electrodes)
            errors = validate(io)
            self.assertEqual(len(errors), 0, errors)

    def test_electrode_id_uniqueness(self):
        device = self.nwbfile.create_device(name='test_device')
        e_group = self.nwbfile.create_electrode_group(name='test_electrode_group',
                                                      description='',
                                                      location='',
                                                      device=device)
        self.nwbfile.add_electrode(id=0, x=0.0, y=0.0, z=0.0, imp=np.nan,
                                   location='loc', filtering='filt', group=e_group)
        with self.assertRaises(ValueError):
            self.nwbfile.add_electrode(id=0, x=0.0, y=0.0, z=0.0, imp=np.nan, location='loc',
                                       filtering='filt', group=e_group)


class TestH5DataIO(TestCase):
    """
    Test that H5DataIO functions correctly on round trip with the HDF5IO backend
    """
    def setUp(self):
        self.nwbfile = NWBFile(session_description='a',
                               identifier='b',
                               session_start_time=datetime(1970, 1, 1, 12, tzinfo=tzutc()))
        self.path = "test_pynwb_io_hdf5_h5dataIO.h5"

    def tearDown(self):
        remove_test_file(self.path)

    def test_gzip_timestamps(self):
        ts = TimeSeries(name='ts_name',
                        data=[1, 2, 3],
                        unit='A',
                        timestamps=H5DataIO(np.array([1., 2., 3.]), compression='gzip'))
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        # confirm that the dataset was indeed compressed
        with File(self.path, 'r') as f:
            self.assertEqual(f['/acquisition/ts_name/timestamps'].compression, 'gzip')

    def test_write_dataset_custom_compress(self):
        a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                     compression='gzip',
                     compression_opts=5,
                     shuffle=True,
                     fletcher32=True)
        ts = TimeSeries(name='ts_name', data=a, unit='A', timestamps=np.arange(5.))
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertTrue(np.all(dset[:] == a.data))
            self.assertEqual(dset.compression, 'gzip')
            self.assertEqual(dset.compression_opts, 5)
            self.assertEqual(dset.shuffle, True)
            self.assertEqual(dset.fletcher32, True)

    def test_write_dataset_custom_chunks(self):
        a = H5DataIO(np.arange(30).reshape(5, 2, 3),
                     chunks=(1, 1, 3))
        ts = TimeSeries(name='ts_name', data=a, unit='A', timestamps=np.arange(5.))
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertTrue(np.all(dset[:] == a.data))
            self.assertEqual(dset.chunks, (1, 1, 3))

    def test_write_dataset_custom_fillvalue(self):
        a = H5DataIO(np.arange(20).reshape(5, 4), fillvalue=-1)
        ts = TimeSeries(name='ts_name', data=a, unit='A', timestamps=np.arange(5.))
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertTrue(np.all(dset[:] == a.data))
            self.assertEqual(dset.fillvalue, -1)

    def test_write_dataset_datachunkiterator_data_and_time(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        tstamps = np.arange(5.)
        tsiter = DataChunkIterator.from_iterable(tstamps)
        ts = TimeSeries(name='ts_name', data=daiter, unit='A', timestamps=tsiter)
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertListEqual(dset[:].tolist(), a.tolist())

    def test_write_dataset_datachunkiterator_data_only(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        tstamps = np.arange(5.)
        ts = TimeSeries(name='ts_name', data=daiter, unit='A', timestamps=tstamps)
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertListEqual(dset[:].tolist(), a.tolist())

    def test_write_dataset_datachunkiterator_with_compression(self):
        a = np.arange(30).reshape(5, 2, 3)
        aiter = iter(a)
        daiter = DataChunkIterator.from_iterable(aiter, buffer_size=2)
        wrapped_daiter = H5DataIO(data=daiter,
                                  compression='gzip',
                                  compression_opts=5,
                                  shuffle=True,
                                  fletcher32=True)
        ts = TimeSeries(name='ts_name', data=wrapped_daiter, unit='A', timestamps=np.arange(5.))
        self.nwbfile.add_acquisition(ts)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile, cache_spec=False)
        with File(self.path, 'r') as f:
            dset = f['/acquisition/ts_name/data']
            self.assertEqual(dset.shape, a.shape)
            self.assertListEqual(dset[:].tolist(), a.tolist())
            self.assertEqual(dset.compression, 'gzip')
            self.assertEqual(dset.compression_opts, 5)
            self.assertEqual(dset.shuffle, True)
            self.assertEqual(dset.fletcher32, True)


class TestNWBHDF5IO(TestCase):
    """Test that file io with NWBHDF5IO works correctly"""

    def setUp(self):
        self.nwbfile = NWBFile(session_description='a test NWB File',
                               identifier='TEST123',
                               session_start_time=datetime(1970, 1, 1, 12, tzinfo=tzutc()))
        self.path = "test_pynwb_io_nwbhdf5.h5"

    def tearDown(self):
        remove_test_file(self.path)

    def test_nwb_version_property(self):
        """Test reading of files with missing nwb_version"""
        # check empty version before write
        with NWBHDF5IO(self.path, 'w') as io:
            self.assertTupleEqual(io.nwb_version, (None, None))
        # write the example file
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile)
        # check behavior for various different version strings
        for ver in [("2.0.5", (2, 0, 5)),
                    ("2.0.5-alpha", (2, 0, 5, "alpha")),
                    ("1.0.4_beta", (1, 0, 4, "beta")),
                    ("bad_version", ("bad", "version", ))]:
            # Set version string
            with File(self.path, mode='a') as io:
                io.attrs['nwb_version'] = ver[0]
            # Assert expected result for nwb_version tuple
            with NWBHDF5IO(self.path, 'r') as io:
                self.assertEqual(io.nwb_version[0], ver[0])
                self.assertTupleEqual(io.nwb_version[1], ver[1])
        # check empty version attribute
        with File(self.path, mode='a') as io:
            del io.attrs['nwb_version']
        with NWBHDF5IO(self.path, 'r') as io:
            self.assertTupleEqual(io.nwb_version, (None, None))
        # check that it works when setting the attribute to a fixed-length numpy-bytes string
        with File(self.path, mode='a') as io:
            io.attrs['nwb_version'] = np.asarray("2.0.5", dtype=np.bytes_)[()]
        with NWBHDF5IO(self.path, 'r') as io:
            self.assertTupleEqual(io.nwb_version, ("2.0.5", (2, 0, 5)))

    def test_check_nwb_version_ok(self):
        """Test that opening a current NWBFile passes the version check"""
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile)
        with NWBHDF5IO(self.path, 'r') as io:
            self.assertIsNotNone(io.nwb_version[0])
            self.assertIsNotNone(io.nwb_version[1])
            self.assertGreater(io.nwb_version[1][0], 1)
            read_file = io.read()
            self.assertContainerEqual(read_file, self.nwbfile)

    def test_check_nwb_version_missing_version(self):
        """Test reading of files with missing nwb_version"""
        # write the example file
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile)
        # remove the version attribute
        with File(self.path, mode='a') as io:
            del io.attrs['nwb_version']
        # test that reading the file without a version strings fails
        with self.assertRaisesWith(
                TypeError,
                "Missing NWB version in file. The file is not a valid NWB file."):
            with NWBHDF5IO(self.path, 'r') as io:
                _ = io.read()
        # test that reading the file when skipping the version check works
        with NWBHDF5IO(self.path, 'r') as io:
            read_file = io.read(skip_version_check=True)
            self.assertContainerEqual(read_file, self.nwbfile)

    def test_check_nwb_version_old_version(self):
        """Test reading of files with version less than 2 """
        # write the example file
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(self.nwbfile)
        # remove the version attribute
        with File(self.path, mode='a') as io:
            io.attrs['nwb_version'] = "1.0.5"
        # test that reading the file without a version strings fails
        with self.assertRaisesWith(
                TypeError,
                "NWB version 1.0.5 not supported. PyNWB supports NWB files version 2 and above."):
            with NWBHDF5IO(self.path, 'r') as io:
                _ = io.read()
        # test that reading the file when skipping the version check works
        with NWBHDF5IO(self.path, 'r') as io:
            read_file = io.read(skip_version_check=True)
            self.assertContainerEqual(read_file, self.nwbfile)

    def test_round_trip_with_path_string(self):
        """Opening a NWBHDF5IO with a path string should work correctly"""
        path_str = self.path
        with NWBHDF5IO(path_str, 'w') as io:
            io.write(self.nwbfile)
        with NWBHDF5IO(path_str, 'r') as io:
            read_file = io.read()
            self.assertContainerEqual(read_file, self.nwbfile)

    def test_round_trip_with_pathlib_path(self):
        """Opening a NWBHDF5IO with a pathlib path should correctly"""

        pathlib_path = Path(self.path)
        with NWBHDF5IO(pathlib_path, 'w') as io:
            io.write(self.nwbfile)
        with NWBHDF5IO(pathlib_path, 'r') as io:
            read_file = io.read()
            self.assertContainerEqual(read_file, self.nwbfile)
