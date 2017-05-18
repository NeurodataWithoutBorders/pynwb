import unittest
import numpy as np
import json
from datetime import datetime
import os

from form.build import GroupBuilder, DatasetBuilder
from form.backends.hdf5 import HDF5IO
from pynwb import get_build_manager

from pynwb import NWBContainer, NWBFile, TimeSeries

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
        self.manager = get_build_manager()
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
        type1 = type(container1)
        type2 = type(container2)
        self.assertEqual(type1, type2)
        for nwbfield in container1.__nwbfields__:
            with self.subTest(nwbfield=nwbfield, container_type=type1.__name__):
                f1 = getattr(container1, nwbfield)
                f2 = getattr(container2, nwbfield)
                if isinstance(f1, tuple) or isinstance(f1, list):
                    if len(f1) > 0 and isinstance(f1[0], NWBContainer):
                        for sub1, sub2 in zip(f1,f2):
                            self.assertContainerEqual(sub1, sub2)
                        continue
                self.assertEqual(f1, f2)

class TestTimeSeriesIO(TestNWBContainerIO):

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

