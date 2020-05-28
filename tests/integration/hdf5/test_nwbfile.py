from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import pandas as pd
import numpy as np

from hdmf.backends.hdf5 import HDF5IO
from hdmf.common import DynamicTable

from pynwb import NWBFile, TimeSeries, NWBHDF5IO, get_manager
from pynwb.file import Subject
from pynwb.epoch import TimeIntervals
from pynwb.ecephys import ElectricalSeries
from pynwb.testing import NWBH5IOMixin, TestCase, remove_test_file


class TestNWBFileHDF5IO(TestCase):
    """ Test reading/writing an NWBFile using HDF5IO """

    def setUp(self):
        """ Set up an NWBFile object with an acquisition TimeSeries, analysis TimeSeries, and a processing module """
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
        self.manager = get_manager()
        self.filename = 'test_nwbfileio.h5'
        self.nwbfile = NWBFile(session_description='a test NWB File',
                               identifier='TEST123',
                               session_start_time=self.start_time,
                               timestamps_reference_time=self.ref_time,
                               file_create_date=self.create_date,
                               experimenter='test experimenter',
                               stimulus_notes='test stimulus notes',
                               data_collection='test data collection notes',
                               experiment_description='test experiment description',
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
        self.ts = TimeSeries(name='test_timeseries', data=list(range(100, 200, 10)),
                             unit='SIunit', timestamps=np.arange(10.), resolution=0.1)
        self.nwbfile.add_acquisition(self.ts)
        self.ts2 = TimeSeries(name='test_timeseries2', data=list(range(200, 300, 10)),
                              unit='SIunit', timestamps=np.arange(10.), resolution=0.1)
        self.nwbfile.add_analysis(self.ts2)
        self.mod = self.nwbfile.create_processing_module('test_module', 'a test module')
        self.ts3 = TimeSeries(name='test_timeseries2', data=list(range(100, 200, 10)),
                              unit='SIunit', timestamps=np.arange(10.), resolution=0.1)
        self.mod.add(self.ts3)

    def tearDown(self):
        """ Delete the created test file """
        remove_test_file(self.filename)

    def test_children(self):
        """ Test that the TimeSeries and processing module are children of their respective parents """
        self.assertIn(self.ts, self.nwbfile.children)
        self.assertIn(self.ts2, self.nwbfile.children)
        self.assertIn(self.mod, self.nwbfile.children)
        self.assertIn(self.ts3, self.mod.children)

    def test_write(self):
        """ Test writing the NWBFile using HDF5IO """
        hdf5io = HDF5IO(self.filename, manager=self.manager, mode='a')
        hdf5io.write(self.nwbfile)
        hdf5io.close()
        # TODO add some asserts

    def test_read(self):
        """ Test reading the NWBFile using HDF5IO """
        hdf5io = HDF5IO(self.filename, manager=self.manager, mode='w')
        hdf5io.write(self.nwbfile)
        hdf5io.close()

        hdf5io = HDF5IO(self.filename, manager=self.manager, mode='r')
        container = hdf5io.read()
        self.assertIsInstance(container, NWBFile)
        self.assertEqual(len(container.acquisition), 1)
        self.assertEqual(len(container.analysis), 1)
        for v in container.acquisition.values():
            self.assertIsInstance(v, TimeSeries)
        self.assertContainerEqual(container, self.nwbfile)
        hdf5io.close()


class TestNWBFileIO(NWBH5IOMixin, TestCase):
    """ Test writing an NWBFile to disk and reading back the file """
    # this uses methods tearDown, test_roundtrip, and validate from NWBH5IOMixin. the rest are overridden

    def setUp(self):
        super().setUp()
        self.start_time = datetime(1970, 1, 1, 12, tzinfo=tzutc())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create_dates = [datetime(2017, 5, 1, 12, tzinfo=tzlocal()),
                             datetime(2017, 5, 2, 13, 0, 0, 1, tzinfo=tzutc()),
                             datetime(2017, 5, 2, 14, tzinfo=tzutc())]

    def setUpContainer(self):
        """ Return a placeholder NWBFile """
        return NWBFile('placeholder', 'placeholder', datetime(1970, 1, 1, 12, tzinfo=tzutc()))

    def build_nwbfile(self):
        """ Create an NWB file """
        self.container = NWBFile(session_description='a test session description for a test NWBFile',
                                 identifier='FILE123',
                                 session_start_time=self.start_time,
                                 file_create_date=self.create_dates,
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
        """ Build and write an NWBFile to disk, read the file, and return the NWBFile """
        self.build_nwbfile()
        self.writer = NWBHDF5IO(self.filename, mode='w')
        self.writer.write(self.container, cache_spec=cache_spec)
        self.writer.close()

        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()
        return self.read_nwbfile

    def addContainer(self, nwbfile):
        """ No-op. roundtripContainer is overridden and no longer uses addContainer """
        pass

    def getContainer(self, nwbfile):
        """ Get the NWBFile object from the given NWBFile """
        return nwbfile


class TestExperimentersConstructorRoundtrip(TestNWBFileIO):
    """ Test that a list of multiple experimenters in a constructor is written to and read from file """

    def build_nwbfile(self):
        description = 'test nwbfile experimenter'
        identifier = 'TEST_experimenter'
        self.nwbfile = NWBFile(session_description=description,
                               identifier=identifier,
                               session_start_time=self.start_time,
                               experimenter=('experimenter1', 'experimenter2'))


class TestExperimentersSetterRoundtrip(TestNWBFileIO):
    """ Test that a list of multiple experimenters in a setter is written to and read from file """

    def build_nwbfile(self):
        description = 'test nwbfile experimenter'
        identifier = 'TEST_experimenter'
        self.nwbfile = NWBFile(session_description=description,
                               identifier=identifier,
                               session_start_time=self.start_time)
        self.nwbfile.experimenter = ('experimenter1', 'experimenter2')


class TestPublicationsConstructorRoundtrip(TestNWBFileIO):
    """ Test that a list of multiple publications in a constructor is written to and read from file """

    def build_nwbfile(self):
        description = 'test nwbfile publications'
        identifier = 'TEST_publications'
        self.nwbfile = NWBFile(session_description=description,
                               identifier=identifier,
                               session_start_time=self.start_time,
                               related_publications=('pub1', 'pub2'))


class TestPublicationsSetterRoundtrip(TestNWBFileIO):
    """ Test that a list of multiple publications in a setter is written to and read from file """

    def build_nwbfile(self):
        description = 'test nwbfile publications'
        identifier = 'TEST_publications'
        self.nwbfile = NWBFile(session_description=description,
                               identifier=identifier,
                               session_start_time=self.start_time)
        self.nwbfile.related_publications = ('pub1', 'pub2')


class TestSubjectIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test Subject """
        return Subject(age='12 mo',
                       description='An unfortunate rat',
                       genotype='WT',
                       sex='M',
                       species='Rattus norvegicus',
                       subject_id='RAT123',
                       weight='2 lbs',
                       date_of_birth=datetime(1970, 1, 1, 12, tzinfo=tzutc()))

    def addContainer(self, nwbfile):
        """ Add the test Subject to the given NWBFile """
        nwbfile.subject = self.container

    def getContainer(self, nwbfile):
        """ Return the test Subject from the given NWBFile """
        return nwbfile.subject


class TestEmptySubjectIO(TestSubjectIO):

    def setUpContainer(self):
        return Subject()


class TestEpochsIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return placeholder epochs object. Tested epochs are added directly to the NWBFile in addContainer """
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):
        """ Add the test epochs to the given NWBFile """
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
        """ Return the test epochs from the given NWBFile """
        return nwbfile.epochs


class TestEpochsIODf(TestEpochsIO):

    def addContainer(self, nwbfile):
        """ Add the test epochs with TimeSeries objects to the given NWBFile """
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

    def test_df_comparison(self):
        """
        Test that the epochs read from file converted to a data frame are the same as the data frame converted
        from the original epochs and the timeseries columns within them are the same
        """
        self.read_container = self.roundtripContainer()
        df_obt = self.read_container.to_dataframe()

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
        # pop the timeseries column out because ts_obt has rows of lists of tuples and ts_exp has rows of lists of lists
        ts_obt = df_obt.pop('timeseries')
        ts_exp = df_exp.pop('timeseries')
        pd.testing.assert_frame_equal(df_exp, df_obt, check_like=True, check_dtype=False)

        # check the timeseries columns match
        for ex, obt in zip(ts_exp, ts_obt):
            self.assertEqual(ex[0][0], obt[0][0])
            self.assertEqual(ex[0][1], obt[0][1])
            self.assertContainerEqual(ex[0][2], obt[0][2])

    def test_df_comparison_no_ts(self):
        """
        Test that the epochs read from file converted to a data frame are the same as the data frame converted
        from the original epochs without a timeseries column
        """
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


class TestTrials(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return placeholder Table for trials. Tested trials are added directly to the NWBFile in addContainer """
        return DynamicTable(name='trials', description='a placeholder table')  # this will get ignored

    def addContainer(self, nwbfile):
        """ Add trials and trial columns to the given NWBFile """
        nwbfile.add_trial_column('foo', 'an int column')
        nwbfile.add_trial_column('bar', 'a float column')
        nwbfile.add_trial_column('baz', 'a string column')
        nwbfile.add_trial_column('qux', 'a boolean column')
        nwbfile.add_trial(start_time=0., stop_time=1., foo=27, bar=28.0, baz="29", qux=True)
        nwbfile.add_trial(start_time=2., stop_time=3., foo=37, bar=38.0, baz="39", qux=False)

        self.container = nwbfile.trials  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test trials table from the given NWBFile """
        return nwbfile.trials


class TestInvalidTimes(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """
        Return placeholder Table for trials. Tested invalid times are added directly to the NWBFile in addContainer
        """
        return DynamicTable(name='invalid times', description='a placeholder table')

    def addContainer(self, nwbfile):
        """ Add invalid times and invalid times columns to the given NWBFile """
        nwbfile.add_invalid_times_column('foo', 'an int column')
        nwbfile.add_invalid_times_column('bar', 'a float column')
        nwbfile.add_invalid_times_column('baz', 'a string column')
        nwbfile.add_invalid_times_column('qux', 'a boolean column')
        nwbfile.add_invalid_time_interval(start_time=0., stop_time=1., foo=27, bar=28.0, baz="29", qux=True)
        nwbfile.add_invalid_time_interval(start_time=2., stop_time=3., foo=37, bar=38.0, baz="39", qux=False)

        self.container = nwbfile.invalid_times  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test invalid times table from the given NWBFile """
        return nwbfile.invalid_times


class TestUnits(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return placeholder table for Units. Tested units are added directly to the NWBFile in addContainer """
        return DynamicTable(name='units', description='a placeholder table')

    def addContainer(self, nwbfile):
        """ Add units and unit columns to the given NWBFile """
        nwbfile.add_unit_column('foo', 'an int column')
        nwbfile.add_unit_column('my_bool', 'a bool column')
        nwbfile.add_unit(foo=27, my_bool=True)
        nwbfile.add_unit(foo=37, my_bool=False)

        self.container = nwbfile.units  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test units table from the given NWBFile """
        return nwbfile.units


class TestDynamicTableFromDataframeIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        return DynamicTable.from_dataframe(pd.DataFrame({
                'a': [[1, 2, 3],
                      [1, 2, 3],
                      [1, 2, 3]],
                'b': ['4', '5', '6']
            }), 'test_table')

    def addContainer(self, nwbfile):
        test_mod = nwbfile.create_processing_module('test', 'desc')
        test_mod.add(self.container)

    def getContainer(self, nwbfile):
        dyn_tab = nwbfile.processing['test'].data_interfaces['test_table']
        return dyn_tab

    def test_to_dataframe(self):
        dyn_tab = self.roundtripContainer()
        dyn_tab.to_dataframe()  # also test 2D column round-trip


class TestElectrodes(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """
        Return placeholder table for electrodes. Tested electrodes are added directly to the NWBFile in addContainer
        """
        return DynamicTable('electrodes', 'a placeholder table')

    def addContainer(self, nwbfile):
        """ Add electrodes and related objects to the given NWBFile """
        self.dev1 = nwbfile.create_device(name='dev1')
        self.group = nwbfile.create_electrode_group(name='tetrode1', description='tetrode description',
                                                    location='tetrode location', device=self.dev1)

        nwbfile.add_electrode(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')

        self.container = nwbfile.electrodes  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test electrodes table from the given NWBFile """
        return nwbfile.electrodes

    def test_roundtrip(self):
        super().test_roundtrip()
        # When comparing the pandas dataframes for the row we drop the 'group' column since the
        # ElectrodeGroup object after reading will naturally have a different address
        pd.testing.assert_frame_equal(self.read_container[0].drop('group', axis=1),
                                      self.container[0].drop('group', axis=1))


class TestElectrodesRegion(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """
        Return placeholder table for electrodes. Tested electrodes are added directly to the NWBFile in addContainer
        """
        return DynamicTable('electrodes', 'a placeholder table')

    def addContainer(self, nwbfile):
        """ Add electrode table region and related objects to the given NWBFile """
        self.dev1 = nwbfile.create_device(name='dev1')
        self.group = nwbfile.create_electrode_group(name='tetrode1', description='tetrode description',
                                                    location='tetrode location', device=self.dev1)

        nwbfile.add_electrode(id=1, x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=2, x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=3, x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')
        nwbfile.add_electrode(id=4, x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=self.group,
                              group_name='tetrode1')

        region = nwbfile.create_electrode_table_region(
            region=tuple([1, 2, 3]),
            name='electrodes',
            description='desc'
        )
        nwbfile.add_acquisition(ElectricalSeries(
            name='test_data',
            data=np.arange(10),
            timestamps=np.arange(10.),
            electrodes=region
        ))

        self.container = region  # override self.container which has the placeholder

    def getContainer(self, nwbfile):
        """ Return the test electrodes table from the given NWBFile """
        self.table = nwbfile.electrodes
        return nwbfile.get_acquisition('test_data').electrodes

    def test_roundtrip(self):
        super().test_roundtrip()
        for ii, item in enumerate(self.read_container):
            pd.testing.assert_frame_equal(self.table[ii+1], item)
