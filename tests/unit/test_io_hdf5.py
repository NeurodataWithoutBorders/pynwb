import unittest
from datetime import datetime
import os
from h5py import File

from pynwb.io.hdf5 import HDF5IO
from pynwb.io import BuildManager
from pynwb import NWBFile, TimeSeries
from pynwb.io.build.builders import GroupBuilder, DatasetBuilder

class TestHDF5Writer(unittest.TestCase):

    def setUp(self):
        self.manager = BuildManager()
        self.path = "test_pynwb_io_hdf5.h5"
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        #self.container = NWBFile('test.nwb', 'a test NWB File', 'TEST123', self.start_time, file_create_date=self.create_date)
        #ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        #self.container.add_raw_timeseries(ts)

        ts_builder = GroupBuilder('test_timeseries',
                                 attributes={'ancestry': 'TimeSeries',
                                             'source': 'example_source',
                                             'neurodata_type': 'TimeSeries',
                                             'help': 'General purpose TimeSeries'},
                                 datasets={'data': DatasetBuilder('data', list(range(100,200,10)),
                                                                  attributes={'unit': 'SIunit',
                                                                              'conversion': 1.0,
                                                                              'resolution': 0.1}),
                                           'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                  attributes={'unit': 'Seconds', 'interval': 1})})
        self.builder = GroupBuilder('root',
                                 groups={'acquisition': GroupBuilder('acquisition', groups={'timeseries': GroupBuilder('timeseries', groups={'test_timeseries': ts_builder}), 'images': GroupBuilder('images')}),
                                         'analysis': GroupBuilder('analysis'),
                                         'epochs': GroupBuilder('epochs'),
                                         'general': GroupBuilder('general'),
                                         'processing': GroupBuilder('processing'),
                                         'stimulus': GroupBuilder('stimulus', groups={'presentation': GroupBuilder('presentation'), 'templates': GroupBuilder('templates')})},
                                 datasets={'file_create_date': DatasetBuilder('file_create_date', [str(self.create_date)]),
                                           'identifier': DatasetBuilder('identifier', 'TEST123'),
                                           'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                                           'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                                           'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
                                 attributes={'neurodata_type': 'NWBFile'})

    def tearDown(self):
        os.remove(self.path)

    def test_write_builder(self):
        writer = HDF5IO(self.path)
        writer.write_builder(self.builder)
        writer.close()
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

    def test_read_builder(self):
        self.maxDiff = None
        io = HDF5IO(self.path)
        io.write_builder(self.builder)
        io.close()
        builder = io.read_builder()
        self.assertEqual(builder, self.builder)
