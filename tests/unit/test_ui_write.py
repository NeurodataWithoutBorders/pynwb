import unittest
import numpy as np
import json
from datetime import datetime

from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.io import BuildManager
from pynwb import NWBFile, TimeSeries

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
        result = self.manager.build(self.container)
        import json
        print('EXPECTED', json.dumps(self.builder, indent=2))
        print('RECIEVED', json.dumps(result, indent=2))
        self.assertDictEqual(result, self.builder)

    @unittest.skip('not now')
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

@unittest.skip('TODO')
class TestTimeSeriesIO(TestNWBContainerIO):

    def setUp(self):
        super(TestTimeSeriesIO, self).setUp()

    def setUpContainer(self):
        self.container = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)

    def setUpBuilder(self):
        self.builder = GroupBuilder('test_timeseries',
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
class TestNWBFileIO(TestNWBContainerIO):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        super(TestNWBFileIO, self).setUp()

    def setUpBuilder(self):
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
                                         'stimulus': GroupBuilder('stimulus', groups={'presentation': GroupBuilder('presentation'), 'template': GroupBuilder('template')})},
                                 datasets={'file_create_date': DatasetBuilder('file_create_date', [str(self.create_date)]),
                                           'identifier': DatasetBuilder('identifier', 'TEST123'),
                                           'session_description': DatasetBuilder('session_description', 'a test NWB file'),
                                           'nwb_version': DatasetBuilder('nwb_version', '1.0.6'),
                                           'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
                                 attributes={'neurodata_type': 'NWBFile'})

    def setUpContainer(self):
        self.container = NWBFile('test.nwb', 'a test NWB File', 'TEST123', self.start_time, file_create_date=self.create_date)
        ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
        self.container.add_raw_timeseries(ts)
        #from pynwb.spec import CATALOG
        #def find_general(spec):
        #    for sub in spec.groups:
        #        if sub.name == 'general':
        #            print('found general, GroupSpec')
        #        else:
        #            find_general(sub)
        #fspec = CATALOG.get_spec('NWBFile')
        #find_general(fspec)
        #print('fspec hash = %s' % hash(fspec))
        #print(json.dumps(fspec, indent=2))

#$        result = self.manager.build(nwbfile)
#$        print(json.dumps(result, indent=2))
