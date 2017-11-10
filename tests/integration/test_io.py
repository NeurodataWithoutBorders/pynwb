import unittest
import six
from datetime import datetime
import os
from h5py import File

from pynwb import NWBFile, TimeSeries, get_manager

from pynwb.form.backends.hdf5 import HDF5IO
from pynwb.form.build import GroupBuilder, DatasetBuilder
from pynwb.form.spec import NamespaceCatalog
from pynwb.spec import NWBGroupSpec, NWBDatasetSpec, NWBNamespace
from pynwb.form.backends.hdf5 import H5SpecReader


class TestHDF5Writer(unittest.TestCase):

    def setUp(self):
        self.manager = get_manager()
        self.path = "test_pynwb_io_hdf5.h5"
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        self.container = NWBFile('a test source', 'a test NWB File', 'TEST123',
                                 self.start_time, file_create_date=self.create_date)
        ts = TimeSeries('test_timeseries', 'example_source',
                        list(range(100, 200, 10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        self.container.add_acquisition(ts)

        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'source': 'example_source',
                                              'neurodata_type': 'TimeSeries',
                                              'help': 'General purpose TimeSeries'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                         attributes={'unit': 'Seconds',
                                                                                     'interval': 1})})
        self.builder = GroupBuilder(
            'root', groups={'acquisition': GroupBuilder(
                'acquisition', groups={'timeseries': GroupBuilder('timeseries', groups={'test_timeseries': ts_builder}),
                                       'images': GroupBuilder('images')}),
                            'analysis': GroupBuilder('analysis'),
                            'epochs': GroupBuilder('epochs'),
                            'general': GroupBuilder('general'),
                            'processing': GroupBuilder('processing'),
                            'stimulus': GroupBuilder(
                                'stimulus',
                                groups={'presentation': GroupBuilder('presentation'),
                                        'templates': GroupBuilder('templates')})},
            datasets={'file_create_date': DatasetBuilder('file_create_date', [str(self.create_date)]),
                      'identifier': DatasetBuilder('identifier', 'TEST123'),
                      'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                      'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                      'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
            attributes={'neurodata_type': 'NWBFile'})

    def tearDown(self):
        os.remove(self.path)

    def test_nwbio(self):
        io = HDF5IO(self.path, self.manager)
        io.write(self.container)
        io.close()
        f = File(self.path)
        self.assertIn('acquisition', f)
        self.assertIn('analysis', f)
        self.assertIn('epochs', f)
        self.assertIn('general', f)
        self.assertIn('processing', f)
        self.assertIn('file_create_date', f)
        self.assertIn('identifier', f)
        self.assertIn('session_description', f)
        self.assertIn('nwb_version', f)
        self.assertIn('session_start_time', f)
        acq = f.get('acquisition')
        self.assertIn('images', acq)
        self.assertIn('timeseries', acq)
        ts = acq.get('timeseries')
        self.assertIn('test_timeseries', ts)

    def test_write_clobber(self):
        io = HDF5IO(self.path, self.manager)
        io.write(self.container)
        io.close()
        f = File(self.path)  # noqa: F841

        if six.PY2:
            assert_file_exists = IOError
        elif six.PY3:
            assert_file_exists = OSError

        with self.assertRaises(assert_file_exists):
            io = HDF5IO(self.path, self.manager, mode='w-')
            io.write(self.container)
            io.close()

    def test_write_cache_spec(self):
        '''
        Round-trip test for writing spec and reading it back in
        '''
        io = HDF5IO(self.path, self.manager)
        io.write(self.container, cache_spec=True)
        io.close()
        f = File(self.path)
        self.assertIn('specifications', f)
        ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
        HDF5IO.load_namespaces(ns_catalog, self.path, namespaces=['core'])
        original_ns = self.manager.namespace_catalog.get_namespace('core')
        cached_ns = ns_catalog.get_namespace('core')
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
