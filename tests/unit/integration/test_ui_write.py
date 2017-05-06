import unittest
import numpy as np
import json
from datetime import datetime
import os

from form.build import GroupBuilder, DatasetBuilder
from form.backends.hdf5 import HDF5IO
from pynwb import BuildManager

from pynwb import NWBFile, TimeSeries

CORE_NAMESPACE = 'core'

class SetEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set) or isinstance(o, frozenset):
            return list(o)
        else:
            return json.JSONEncoder.default(self, o)

class TestNWBContainerIO(unittest.TestCase):

    def setUp(self):
        if type(self) == TestNWBContainerIO:
            raise unittest.SkipTest('TestNWBContainerIO must be extended with setUpBuilder and setUpContainer implemented')
        self.manager = BuildManager()
        self.setUpContainer()
        self.setUpBuilder()

    def test_build(self):
        self.maxDiff = None
        result = self.manager.build(self.container)
        self.assertDictEqual(result, self.builder)

    def test_construct(self):
        result = self.manager.construct(self.builder)
        self.assertContainerEqual(result, self.container)

    def setUpBuilder(self):
        ''' Should set the attribute 'builder' on self '''
        if isinstance(self, TestNWBContainerIO):
            raise unittest.SkipTest('Cannot run test unless setUpBuilder is implemented')

    def setUpContainer(self):
        ''' Should set the attribute 'container' on self '''
        if isinstance(self, TestNWBContainerIO):
            raise unittest.SkipTest('Cannot run test unless setUpContainer is implemented')

    def assertContainerEqual(self, container1, container2):
        pass

class TestTimeSeriesIO(TestNWBContainerIO):

    def setUp(self):
        super(TestTimeSeriesIO, self).setUp()

    def setUpContainer(self):
        self.container = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)

    def setUpBuilder(self):
        self.builder = GroupBuilder('test_timeseries',
                                attributes={'ancestry': 'TimeSeries',
                                            'source': 'example_source',
                                            'namespace': CORE_NAMESPACE,
                                            'neurodata_type': 'TimeSeries',
                                            'help': 'General purpose TimeSeries'},
                                datasets={'data': DatasetBuilder('data', list(range(100,200,10)),
                                                                 attributes={'unit': 'SIunit',
                                                                             'conversion': 1.0,
                                                                             'resolution': 0.1}),
                                          'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                 attributes={'unit': 'Seconds', 'interval': 1})})
class TestNWBFileIO(TestNWBContainerIO):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        super(TestNWBFileIO, self).setUp()
        self.path = "test_pynwb_io_hdf5.h5"

    def setUpBuilder(self):
        ts_builder = GroupBuilder('test_timeseries',
                                 attributes={'ancestry': 'TimeSeries',
                                             'source': 'example_source',
                                             'namespace': CORE_NAMESPACE,
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
                                 attributes={'namespace': CORE_NAMESPACE, 'neurodata_type': 'NWBFile'})

    def setUpContainer(self):
        self.container = NWBFile('test.nwb', 'a test NWB File', 'TEST123', self.start_time, file_create_date=self.create_date)
        ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        self.container.add_raw_timeseries(ts)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_write(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()

    def test_read(self):
        hdf5io = HDF5IO('dontremove.h5', self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        container = hdf5io.read()
        print(container)
        print(container.raw_data)
        hdf5io.close()

