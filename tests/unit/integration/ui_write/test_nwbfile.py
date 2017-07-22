import unittest
import numpy as np
import json
from datetime import datetime
import os

from form.build import GroupBuilder, DatasetBuilder
from form.backends.hdf5 import HDF5IO

from pynwb import NWBFile, TimeSeries
from pynwb.ecephys import Clustering

from .  import base

class TestNWBFileIO(base.TestNWBContainerIO):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        super(TestNWBFileIO, self).setUp()
        self.path = "test_pynwb_io_hdf5.h5"

    def setUpBuilder(self):
        ts_builder = GroupBuilder('test_timeseries',
                                 attributes={'ancestry': 'TimeSeries',
                                             'source': 'example_source',
                                             'namespace': base.CORE_NAMESPACE,
                                             'neurodata_type': 'TimeSeries',
                                             'data_link': list(),
                                             'timestamp_link': list(),
                                             'help': 'General time series object'},
                                 datasets={'data': DatasetBuilder('data', list(range(100,200,10)),
                                                                  attributes={'unit': 'SIunit',
                                                                              'conversion': 1.0,
                                                                              'resolution': 0.1}),
                                           'num_samples': DatasetBuilder('num_samples', 10),
                                           'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                  attributes={'unit': 'Seconds', 'interval': 1})})

        module_builder = GroupBuilder('test_module',
                                 attributes={'namespace': base.CORE_NAMESPACE,
                                             'neurodata_type': 'Module',
                                             'interfaces': ['Clustering'],
                                             'description': 'a test module'},
                                 groups={'Clustering': GroupBuilder('Clustering',
                                         attributes={
                                            'help': 'Clustered spike data, whether from automatic clustering tools (eg, klustakwik) or as a result of manual sorting',
                                            'source': "an example source for Clustering",
                                            'neurodata_type': 'Clustering',
                                            'namespace': base.CORE_NAMESPACE},
                                         datasets={
                                            'cluster_nums': DatasetBuilder('cluster_nums', [0,1,2]),
                                            'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
                                            'times': DatasetBuilder('times', list(range(10,61,10))),
                                            'peak_over_rms': DatasetBuilder('peak_over_rms', [100, 101, 102]),
                                            'description': DatasetBuilder('description', "A fake Clustering interface")})})


        self.builder = GroupBuilder('root',
                                 groups={'acquisition': GroupBuilder('acquisition', groups={'timeseries': GroupBuilder('timeseries', groups={'test_timeseries': ts_builder}), 'images': GroupBuilder('images')}),
                                         'analysis': GroupBuilder('analysis'),
                                         'epochs': GroupBuilder('epochs', attributes={'tags': list()}),
                                         'general': GroupBuilder('general'),
                                         'processing': GroupBuilder('processing', groups={'test_module': module_builder}),
                                         'stimulus': GroupBuilder('stimulus', groups={'presentation': GroupBuilder('presentation'), 'templates': GroupBuilder('templates')})},
                                 datasets={'file_create_date': DatasetBuilder('file_create_date', [str(self.create_date)]),
                                           'identifier': DatasetBuilder('identifier', 'TEST123'),
                                           'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                                           'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                                           'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
                                 attributes={'namespace': base.CORE_NAMESPACE, 'neurodata_type': 'NWBFile'})

    def setUpContainer(self):
        self.container = NWBFile('test.nwb', 'a test NWB File', 'TEST123', self.start_time, file_create_date=self.create_date)
        ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        self.container.add_raw_timeseries(ts)
        mod = self.container.create_processing_module('test_module', 'a test module')
        mod.add_interface(Clustering("an example source for Clustering", "A fake Clustering interface", [0, 1, 2, 0, 1, 2], [100, 101, 102], list(range(10,61,10))))

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_write(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        #TODO add some asserts

    def test_read(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        container = hdf5io.read()
        self.assertIsInstance(container, NWBFile)
        raw_ts = container.raw_timeseries
        self.assertEqual(len(raw_ts), 1)
        self.assertIsInstance(raw_ts[0], TimeSeries)
        hdf5io.close()
