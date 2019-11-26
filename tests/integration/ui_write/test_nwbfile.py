import os
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import pandas as pd
import numpy as np

from hdmf.backends.hdf5 import HDF5IO

from pynwb import NWBFile, TimeSeries, get_manager
from pynwb.file import Subject
from pynwb.epoch import TimeIntervals
from pynwb.testing import TestMapNWBContainer, TestMapRoundTrip, TestDataInterfaceIO


class TestNWBFileIO(TestMapNWBContainer):

    def setUp(self):
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        super(TestNWBFileIO, self).setUp()
        self.path = "test_pynwb_io_hdf5.h5"

    def setUpContainer(self):
        container = NWBFile('a test NWB File', 'TEST123',
                            self.start_time,
                            timestamps_reference_time=self.ref_time,
                            file_create_date=self.create_date,
                            experimenter='test experimenter',
                            stimulus_notes='test stimulus notes',
                            experiment_description='test experiment description',
                            data_collection='test data collection notes',
                            institution='nomad',
                            lab='nolab',
                            notes='nonotes',
                            pharmacology='nopharmacology',
                            protocol='noprotocol',
                            related_publications='nopubs',
                            session_id='007',
                            slices='noslices',
                            source_script='nosources',
                            surgery='nosurgery',
                            virus='novirus',
                            source_script_file_name='nofilename')
        self.ts = TimeSeries('test_timeseries', list(range(100, 200, 10)),
                             'SIunit', timestamps=list(range(10)), resolution=0.1)
        container.add_acquisition(self.ts)
        self.ts2 = TimeSeries('test_timeseries2', list(range(200, 300, 10)),
                              'SIunit', timestamps=list(range(10)), resolution=0.1)
        container.add_analysis(self.ts2)
        self.mod = container.create_processing_module('test_module',
                                                      'a test module')
        self.ts2 = TimeSeries('test_timeseries2', list(range(100, 200, 10)),
                              'SIunit', timestamps=list(range(10)), resolution=0.1)
        self.mod.add(self.ts2)
        return container

    def test_children(self):
        self.assertIn(self.ts, self.container.children)
        self.assertIn(self.mod, self.container.children)
        self.assertIn(self.ts2, self.mod.children)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_write(self):
        hdf5io = HDF5IO(self.path, manager=self.manager, mode='a')
        hdf5io.write(self.container)
        hdf5io.close()
        # TODO add some asserts

    def test_read(self):
        hdf5io = HDF5IO(self.path, manager=self.manager, mode='w')
        hdf5io.write(self.container)
        hdf5io.close()
        hdf5io = HDF5IO(self.path, manager=self.manager, mode='r')
        container = hdf5io.read()
        self.assertIsInstance(container, NWBFile)
        raw_ts = container.acquisition
        self.assertEqual(len(raw_ts), 1)
        self.assertEqual(len(container.analysis), 1)
        for v in raw_ts.values():
            self.assertIsInstance(v, TimeSeries)
        hdf5io.close()


class TestSubjectIO(TestDataInterfaceIO):

    def setUpContainer(self):
        return Subject(age='12 mo',
                       description='An unfortunate rat',
                       genotype='WT',
                       sex='M',
                       species='Rattus norvegicus',
                       subject_id='RAT123',
                       weight='2 lbs',
                       date_of_birth=datetime(1970, 1, 1, 12, tzinfo=tzutc()))

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.subject = self.container

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.subject


class TestEmptySubjectIO(TestSubjectIO):

    def setUpContainer(self):
        return Subject()


class TestEpochsRoundtrip(TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):
        nwbfile.add_epoch_column(
            name='temperature',
            description='average temperture (c) during epoch'
        )

        nwbfile.add_epoch(
            start_time=5.3,
            stop_time=6.1,
            timeseries=[],
            tags='ambient',
            temperature=26.4,
        )

        # reset the thing
        self.container = nwbfile.epochs

    def getContainer(self, nwbfile):
        return nwbfile.epochs


class TestEpochsRoundtripDf(TestMapRoundTrip):

    def setUpContainer(self):
        # this will get ignored
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):
        tsa, tsb = [
            TimeSeries(name='a', data=np.arange(11), unit='flubs', timestamps=np.linspace(0, 1, 11)),
            TimeSeries(name='b', data=np.arange(13), unit='flubs', timestamps=np.linspace(0.1, 5, 13)),
        ]

        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)

        nwbfile.epochs = TimeIntervals.from_dataframe(
            pd.DataFrame({
                'foo': [1, 2, 3, 4],
                'bar': ['fish', 'fowl', 'dog', 'cat'],
                'start_time': [0.2, 0.25, 0.30, 0.35],
                'stop_time': [0.25, 0.30, 0.40, 0.45],
                'timeseries': [[(2, 1, tsa)],
                               [(3, 1, tsa)],
                               [(3, 1, tsa)],
                               [(4, 1, tsa)]],
                'tags': [[''], [''], ['fizz', 'buzz'], ['qaz']]
            }),
            'epochs',
            columns=[
                {'name': 'foo', 'description': 'a column of integers'},
                {'name': 'bar', 'description': 'a column of strings'},
            ]
        )

        # reset the thing
        self.container = nwbfile.epochs

    def getContainer(self, nwbfile):
        return nwbfile.epochs

    def test_df_comparison(self):
        self.read_container = self.roundtripContainer()

        tsa = self.read_nwbfile.get_acquisition('a')
        df_exp = pd.DataFrame({
                'foo': [1, 2, 3, 4],
                'bar': ['fish', 'fowl', 'dog', 'cat'],
                'start_time': [0.2, 0.25, 0.30, 0.35],
                'stop_time': [0.25, 0.30, 0.40, 0.45],
                'timeseries': [[(2, 1, tsa)],
                               [(3, 1, tsa)],
                               [(3, 1, tsa)],
                               [(4, 1, tsa)]],
                'tags': [[''], [''], ['fizz', 'buzz'], ['qaz']]
            },
            index=pd.Index(np.arange(4), name='id')
        )
        ts_exp = df_exp.pop('timeseries')

        df_obt = self.read_container.to_dataframe()
        ts_obt = df_obt.pop('timeseries')

        pd.testing.assert_frame_equal(df_exp, df_obt, check_like=True, check_dtype=False)
        for ex, obt in zip(ts_exp, ts_obt):
            assert ex[0][0] == obt[0][0]
            assert ex[0][1] == obt[0][1]
            self.assertContainerEqual(ex[0][2], obt[0][2])

    def test_df_comparison_no_ts(self):
        self.read_container = self.roundtripContainer()

        df_exp = pd.DataFrame({
                'foo': [1, 2, 3, 4],
                'bar': ['fish', 'fowl', 'dog', 'cat'],
                'start_time': [0.2, 0.25, 0.30, 0.35],
                'stop_time': [0.25, 0.30, 0.40, 0.45],
                'tags': [[''], [''], ['fizz', 'buzz'], ['qaz']]
            },
            index=pd.Index(np.arange(4), name='id')
        )

        df_obt = self.read_container.to_dataframe(exclude=set(['timeseries', 'timeseries_index']))
        pd.testing.assert_frame_equal(df_exp, df_obt, check_like=True, check_dtype=False)


class TestNWBFileRoundtrip(TestMapRoundTrip):

    def setUp(self):
        super(TestMapRoundTrip, self).setUp()
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create = [datetime(2017, 5, 1, 12, tzinfo=tzlocal()),
                       datetime(2017, 5, 2, 13, 0, 0, 1, tzinfo=tzutc()),
                       datetime(2017, 5, 2, 14, tzinfo=tzutc())]
        self.filename = 'test_nwbfile.nwb'
        self.writer = None
        self.reader = None

    def setUpContainer(self):
        pass

    def build_nwbfile(self):
        self.nwbfile = NWBFile('a test session description for a test NWBFile',
                               'FILE123',
                               self.start_time,
                               file_create_date=self.create,
                               timestamps_reference_time=self.ref_time,
                               experimenter='A test experimenter',
                               lab='a test lab',
                               institution='a test institution',
                               experiment_description='a test experiment description',
                               session_id='test1',
                               notes='my notes',
                               pharmacology='drugs',
                               protocol='protocol',
                               related_publications='my pubs',
                               slices='my slices',
                               surgery='surgery',
                               virus='a virus',
                               source_script='noscript',
                               source_script_file_name='nofilename',
                               stimulus_notes='test stimulus notes',
                               data_collection='test data collection notes',
                               keywords=('these', 'are', 'keywords'))

    def roundtripContainer(self, cache_spec=False):
        self.build_nwbfile()
        self.writer = HDF5IO(self.filename, manager=get_manager(), mode='w')
        self.writer.write(self.nwbfile, cache_spec=cache_spec)
        self.writer.close()
        self.reader = HDF5IO(self.filename, manager=get_manager(), mode='r')
        self.read_nwbfile = self.reader.read()

    def test_roundtrip(self):
        self.roundtripContainer()
        self.assertNotEqual(id(self.nwbfile), id(self.read_nwbfile))
        self.assertContainerEqual(self.read_nwbfile, self.nwbfile)
        self.validate()


class TestExperimentersConstructorRoundtrip(TestNWBFileRoundtrip):
    """Test that a list of multiple experimenters in a constructor is written to and read from file"""

    def build_nwbfile(self):
        description = 'test nwbfile experimenter'
        identifier = 'TEST_experimenter'
        self.nwbfile = NWBFile(description, identifier, self.start_time,
                               experimenter=('experimenter1', 'experimenter2'))


class TestExperimentersSetterRoundtrip(TestNWBFileRoundtrip):
    """Test that a list of multiple experimenters in a setter is written to and read from file"""

    def build_nwbfile(self):
        description = 'test nwbfile experimenter'
        identifier = 'TEST_experimenter'
        self.nwbfile = NWBFile(description, identifier, self.start_time)
        self.nwbfile.experimenter = ('experimenter1', 'experimenter2')


class TestPublicationsConstructorRoundtrip(TestNWBFileRoundtrip):
    """Test that a list of multiple publications in a constructor is written to and read from file"""

    def build_nwbfile(self):
        description = 'test nwbfile publications'
        identifier = 'TEST_publications'
        self.nwbfile = NWBFile(description, identifier, self.start_time,
                               related_publications=('pub1', 'pub2'))


class TestPublicationsSetterRoundtrip(TestNWBFileRoundtrip):
    """Test that a list of multiple publications in a setter is written to and read from file"""

    def build_nwbfile(self):
        description = 'test nwbfile publications'
        identifier = 'TEST_publications'
        self.nwbfile = NWBFile(description, identifier, self.start_time)
        self.nwbfile.related_publications = ('pub1', 'pub2')
