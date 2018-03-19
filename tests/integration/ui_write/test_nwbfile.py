from datetime import datetime
import os

from pynwb.form.build import GroupBuilder, DatasetBuilder
from pynwb.form.backends.hdf5 import HDF5IO

from pynwb import NWBFile, TimeSeries
from pynwb.file import Subject
from pynwb.ecephys import Clustering

from . import base


class TestNWBFileIO(base.TestMapNWBContainer):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, 0, 0)
        self.create_date = datetime(2017, 4, 15, 12, 0, 0)
        super(TestNWBFileIO, self).setUp()
        self.path = "test_pynwb_io_hdf5.h5"

    def setUpBuilder(self):
        ts_builder = GroupBuilder('test_timeseries',
                                  attributes={'source': 'example_source',
                                              'namespace': base.CORE_NAMESPACE,
                                              'neurodata_type': 'TimeSeries',
                                              'comments': 'no comments',
                                              'description': 'no description',
                                              'help': 'General time series object'},
                                  datasets={'data': DatasetBuilder('data', list(range(100, 200, 10)),
                                                                   attributes={'unit': 'SIunit',
                                                                               'conversion': 1.0,
                                                                               'resolution': 0.1}),
                                            'timestamps': DatasetBuilder('timestamps', list(range(10)),
                                                                         attributes={'unit': 'Seconds',
                                                                                     'interval': 1})})

        module_builder = GroupBuilder('test_module',
                                      attributes={'namespace': base.CORE_NAMESPACE,
                                                  'neurodata_type': 'ProcessingModule',
                                                  'source': 'a test source for a ProcessingModule',
                                                  'help': 'A collection of analysis outputs from processing of data',
                                                  'description': 'a test module'},
                                      groups={
                                          'Clustering':
                                          GroupBuilder('Clustering',
                                                       attributes={
                                                           'help': 'Clustered spike data, whether from automatic clustering tools (eg, klustakwik) or as a result of manual sorting',  # noqa: E501
                                                           'source': "an example source for Clustering",
                                                           'neurodata_type': 'Clustering',
                                                           'namespace': base.CORE_NAMESPACE},
                                                       datasets={
                                                           'num': DatasetBuilder('num', [0, 1, 2, 0, 1, 2]),
                                                           'times': DatasetBuilder('times', list(range(10, 61, 10))),
                                                           'peak_over_rms':
                                                           DatasetBuilder('peak_over_rms', [100, 101, 102]),
                                                           'description':
                                                           DatasetBuilder('description',
                                                                          "A fake Clustering interface")})})

        return GroupBuilder('root',
                            groups={'acquisition': GroupBuilder(
                                'acquisition',
                                groups={'test_timeseries': ts_builder}),
                                    'analysis': GroupBuilder('analysis'),
                                    'epochs': GroupBuilder('epochs'),
                                    'general': GroupBuilder('general'),
                                    'processing': GroupBuilder('processing', groups={'test_module': module_builder}),
                                    'stimulus': GroupBuilder(
                                        'stimulus',
                                        groups={'presentation':
                                                GroupBuilder('presentation'),
                                                'templates': GroupBuilder('templates')})},
                            datasets={
                                'file_create_date':
                                DatasetBuilder('file_create_date', [str(self.create_date)]),
                                'identifier': DatasetBuilder('identifier', 'TEST123'),
                                'session_description': DatasetBuilder('session_description', 'a test NWB File'),
                                'nwb_version': DatasetBuilder('nwb_version', '1.2.0'),
                                'session_start_time': DatasetBuilder('session_start_time', str(self.start_time))},
                            attributes={'namespace': base.CORE_NAMESPACE,
                                        'neurodata_type': 'NWBFile',
                                        'help': 'an NWB:N file for storing cellular-based neurophysiology data',
                                        'source': 'a test source'})

    def setUpContainer(self):
        container = NWBFile('a test source', 'a test NWB File', 'TEST123',
                            self.start_time, file_create_date=self.create_date)
        ts = TimeSeries('test_timeseries', 'example_source', list(range(100, 200, 10)),
                        'SIunit', timestamps=list(range(10)), resolution=0.1)
        container.add_acquisition(ts)
        mod = container.create_processing_module('test_module', 'a test source for a ProcessingModule', 'a test module')
        mod.add_container(Clustering("an example source for Clustering",
                                     "A fake Clustering interface", [0, 1, 2, 0, 1, 2], [100, 101, 102],
                                     list(range(10, 61, 10))))
        return container

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_write(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        # TODO add some asserts

    def test_read(self):
        hdf5io = HDF5IO(self.path, self.manager)
        hdf5io.write(self.container)
        hdf5io.close()
        hdf5io = HDF5IO(self.path, self.manager)
        container = hdf5io.read()
        self.assertIsInstance(container, NWBFile)
        raw_ts = container.acquisition
        self.assertEqual(len(raw_ts), 1)
        for v in raw_ts.values():
            self.assertIsInstance(v, TimeSeries)
        hdf5io.close()


class TestSubjectIO(base.TestDataInterfaceIO):

    def setUpContainer(self):
        return Subject(age='12 mo',
                       description='An unfortunate rat',
                       genotype='WT',
                       sex='M',
                       species='Rattus norvegicus',
                       subject_id='RAT123',
                       weight='2 lbs',
                       source='Subject integration test')

    def setUpBuilder(self):
        return GroupBuilder('subject',
                            attributes={'source': 'Subject integration test',
                                        'namespace': base.CORE_NAMESPACE,
                                        'neurodata_type': 'Subject',
                                        'help': 'Information about the subject'},
                            datasets={'age': DatasetBuilder('age', '12 mo'),
                                      'description': DatasetBuilder('description', 'An unfortunate rat'),
                                      'genotype': DatasetBuilder('genotype', 'WT'),
                                      'sex': DatasetBuilder('sex', 'M'),
                                      'species': DatasetBuilder('species', 'Rattus norvegicus'),
                                      'subject_id': DatasetBuilder('subject_id', 'RAT123'),
                                      'weight': DatasetBuilder('weight', '2 lbs')})

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.subject = self.container

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.subject
