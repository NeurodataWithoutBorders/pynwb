''' Tests for NWBFile '''
import unittest2 as unittest
import six
import numpy as np
import os

from datetime import datetime
from dateutil.tz import tzlocal, tzutc

from pynwb import NWBFile, TimeSeries
from pynwb import NWBHDF5IO
from pynwb.file import Subject, ElectrodeTable


class NWBFileTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
        self.create = [datetime(2017, 5, 1, 12, tzinfo=tzlocal()),
                       datetime(2017, 5, 2, 13, 0, 0, 1, tzinfo=tzutc()),
                       datetime(2017, 5, 2, 14, tzinfo=tzutc())]
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile('a test session description for a test NWBFile',
                               'FILE123',
                               self.start,
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

    def test_constructor(self):
        self.assertEqual(self.nwbfile.session_description, 'a test session description for a test NWBFile')
        self.assertEqual(self.nwbfile.identifier, 'FILE123')
        self.assertEqual(self.nwbfile.session_start_time, self.start)
        self.assertEqual(self.nwbfile.file_create_date, self.create)
        self.assertEqual(self.nwbfile.lab, 'a test lab')
        self.assertEqual(self.nwbfile.experimenter, 'A test experimenter')
        self.assertEqual(self.nwbfile.institution, 'a test institution')
        self.assertEqual(self.nwbfile.experiment_description, 'a test experiment description')
        self.assertEqual(self.nwbfile.session_id, 'test1')
        self.assertEqual(self.nwbfile.stimulus_notes, 'test stimulus notes')
        self.assertEqual(self.nwbfile.data_collection, 'test data collection notes')
        self.assertEqual(self.nwbfile.source_script, 'noscript')
        self.assertEqual(self.nwbfile.source_script_file_name, 'nofilename')
        self.assertEqual(self.nwbfile.keywords, ('these', 'are', 'keywords'))
        self.assertEqual(self.nwbfile.timestamps_reference_time, self.ref_time)

    def test_create_electrode_group(self):
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        d = self.nwbfile.create_device('a fake device')
        elecgrp = self.nwbfile.create_electrode_group(name, desc, loc, d)
        self.assertEqual(elecgrp.description, desc)
        self.assertEqual(elecgrp.location, loc)
        self.assertIs(elecgrp.device, d)

    def test_create_electrode_group_invalid_index(self):
        """
        Test the case where the user creates an electrode table region with
        indexes that are out of range of the amount of electrodes added.
        """
        nwbfile = NWBFile('a', 'b', datetime.now(tzlocal()))
        device = nwbfile.create_device('a')
        elecgrp = nwbfile.create_electrode_group('a', 'b', device=device, location='a')
        for i in range(4):
            nwbfile.add_electrode(np.nan, np.nan, np.nan, np.nan, 'a', 'a', elecgrp, id=i)
        with self.assertRaises(IndexError) as err:
            nwbfile.create_electrode_table_region(list(range(6)), 'test')
        self.assertTrue('out of range' in str(err.exception))

    def test_epoch_tags(self):
        tags1 = ['t1', 't2']
        tags2 = ['t3', 't4']
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        expected_tags = tags1 + tags2
        self.nwbfile.add_epoch(0.0, 1.0, tags1, ts)
        self.nwbfile.add_epoch(0.0, 1.0, tags2, ts)
        tags = self.nwbfile.epoch_tags
        six.assertCountEqual(self, expected_tags, tags)

    def test_add_acquisition(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.acquisition), 1)

    def test_add_stimulus(self):
        self.nwbfile.add_stimulus(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                             'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus), 1)

    def test_add_stimulus_template(self):
        self.nwbfile.add_stimulus_template(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                      'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus_template), 1)

    def test_add_acquisition_check_dups(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        with self.assertRaises(ValueError):
            self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                    'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))

    def test_get_acquisition_empty(self):
        with self.assertRaisesRegex(ValueError, "acquisition of NWBFile 'root' is empty"):
            self.nwbfile.get_acquisition()

    def test_get_acquisition_multiple_elements(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.nwbfile.add_acquisition(TimeSeries('test_ts2', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "more than one element in acquisition of NWBFile 'root' -- must specify a name"
        with self.assertRaisesRegex(ValueError,  msg):
            self.nwbfile.get_acquisition()

    def test_add_acquisition_invalid_name(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "'TEST_TS' not found in acquisition of NWBFile 'root'"
        with self.assertRaisesRegex(KeyError, msg):
            self.nwbfile.get_acquisition("TEST_TS")

    def test_set_electrode_table(self):
        table = ElectrodeTable()  # noqa: F405
        dev1 = self.nwbfile.create_device('dev1')  # noqa: F405
        group = self.nwbfile.create_electrode_group('tetrode1',
                                                    'tetrode description', 'tetrode location', dev1)
        table.add_row(x=1.0, y=2.0, z=3.0, imp=-1.0, location='CA1', filtering='none', group=group,
                      group_name='tetrode1')
        table.add_row(x=1.0, y=2.0, z=3.0, imp=-2.0, location='CA1', filtering='none', group=group,
                      group_name='tetrode1')
        table.add_row(x=1.0, y=2.0, z=3.0, imp=-3.0, location='CA1', filtering='none', group=group,
                      group_name='tetrode1')
        table.add_row(x=1.0, y=2.0, z=3.0, imp=-4.0, location='CA1', filtering='none', group=group,
                      group_name='tetrode1')
        self.nwbfile.set_electrode_table(table)
        self.assertIs(self.nwbfile.ec_electrodes, table)
        self.assertIs(table.parent, self.nwbfile)

    def test_add_unit_column(self):
        self.nwbfile.add_unit_column('unit_type', 'the type of unit')
        self.assertEqual(self.nwbfile.units.colnames, ('unit_type',))

    def test_add_unit(self):
        self.nwbfile.add_unit(id=1)
        self.assertEqual(len(self.nwbfile.units), 1)
        self.nwbfile.add_unit(id=2)
        self.nwbfile.add_unit(id=3)
        self.assertEqual(len(self.nwbfile.units), 3)

    def test_add_trial_column(self):
        self.nwbfile.add_trial_column('trial_type', 'the type of trial')
        self.assertEqual(self.nwbfile.trials.colnames, ('start_time', 'stop_time', 'trial_type'))

    def test_add_trial(self):
        self.nwbfile.add_trial(start_time=10.0, stop_time=20.0)
        self.assertEqual(len(self.nwbfile.trials), 1)
        self.nwbfile.add_trial(start_time=30.0, stop_time=40.0)
        self.nwbfile.add_trial(start_time=50.0, stop_time=70.0)
        self.assertEqual(len(self.nwbfile.trials), 3)

    def test_add_invalid_times_column(self):
        self.nwbfile.add_invalid_times_column('comments', 'description of reason for omitting time')
        self.assertEqual(self.nwbfile.invalid_times.colnames, ('start_time', 'stop_time', 'comments'))

    def test_add_invalid_time_interval(self):

        self.nwbfile.add_invalid_time_interval(start_time=0.0, stop_time=12.0)
        self.assertEqual(len(self.nwbfile.invalid_times), 1)
        self.nwbfile.add_invalid_time_interval(start_time=15.0, stop_time=16.0)
        self.nwbfile.add_invalid_time_interval(start_time=17.0, stop_time=20.5)
        self.assertEqual(len(self.nwbfile.invalid_times), 3)

    def test_add_invalid_time_w_ts(self):
        ts = TimeSeries(name='name', data=[1.2], rate=1.0, unit='na')
        self.nwbfile.add_invalid_time_interval(start_time=18.0, stop_time=20.6,
                                               timeseries=ts, tags=('hi', 'there'))

    def test_add_electrode(self):
        dev1 = self.nwbfile.create_device('dev1')  # noqa: F405
        group = self.nwbfile.create_electrode_group('tetrode1',
                                                    'tetrode description', 'tetrode location', dev1)
        self.nwbfile.add_electrode(1.0, 2.0, 3.0, -1.0, 'CA1',
                                   'none', group=group, id=1)
        self.assertEqual(self.nwbfile.ec_electrodes[0][0], 1)
        self.assertEqual(self.nwbfile.ec_electrodes[0][1], 1.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][2], 2.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][3], 3.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][4], -1.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][5], 'CA1')
        self.assertEqual(self.nwbfile.ec_electrodes[0][6], 'none')
        self.assertEqual(self.nwbfile.ec_electrodes[0][7], group)

    def test_all_children(self):
        ts1 = TimeSeries('test_ts1', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.nwbfile.add_acquisition(ts1)
        self.nwbfile.add_acquisition(ts2)
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        device = self.nwbfile.create_device('a fake device')
        elecgrp = self.nwbfile.create_electrode_group(name, desc, loc, device)
        children = self.nwbfile.all_children()
        self.assertIn(ts1, children)
        self.assertIn(ts2, children)
        self.assertIn(device, children)
        self.assertIn(elecgrp, children)

    def test_fail_if_source_script_file_name_without_source_script(self):
        with self.assertRaises(ValueError):
            # <-- source_script_file_name without source_script is not allowed
            NWBFile('a test session description for a test NWBFile', 'FILE123', self.start,
                    source_script=None,
                    source_script_file_name='nofilename')


class SubjectTest(unittest.TestCase):
    def setUp(self):
        self.subject = Subject(age='12 mo',
                               description='An unfortunate rat',
                               genotype='WT',
                               sex='M',
                               species='Rattus norvegicus',
                               subject_id='RAT123',
                               weight='2 lbs')
        self.start = datetime(2017, 5, 1, 12, tzinfo=tzlocal())
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile('a test session description for a test NWBFile',
                               'FILE123',
                               self.start,
                               experimenter='A test experimenter',
                               lab='a test lab',
                               institution='a test institution',
                               experiment_description='a test experiment description',
                               session_id='test1',
                               subject=self.subject)

    def test_constructor(self):
        self.assertEqual(self.subject.age, '12 mo')
        self.assertEqual(self.subject.description, 'An unfortunate rat')
        self.assertEqual(self.subject.genotype, 'WT')
        self.assertEqual(self.subject.sex, 'M')
        self.assertEqual(self.subject.species, 'Rattus norvegicus')
        self.assertEqual(self.subject.subject_id, 'RAT123')
        self.assertEqual(self.subject.weight, '2 lbs')

    def test_nwbfile_constructor(self):
        self.assertIs(self.nwbfile.subject, self.subject)


class TestCacheSpec(unittest.TestCase):

    def setUp(self):
        self.path = 'unittest_cached_spec.nwb'

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_simple(self):
        nwbfile = NWBFile(' ', ' ',
                          datetime.now(tzlocal()),
                          file_create_date=datetime.now(tzlocal()),
                          institution='University of California, San Francisco',
                          lab='Chang Lab')
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile, cache_spec=True)
        reader = NWBHDF5IO(self.path, 'r', load_namespaces=True)
        nwbfile = reader.read()


class TestTimestampsRefDefault(unittest.TestCase):
    def setUp(self):
        self.start_time = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.nwbfile = NWBFile('test session description',
                               'TEST123',
                               self.start_time)

    def test_reftime_default(self):
        # 'timestamps_reference_time' should default to 'session_start_time'
        self.assertEqual(self.nwbfile.timestamps_reference_time, self.start_time)


class TestTimestampsRefAware(unittest.TestCase):
    def setUp(self):
        self.start_time = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal())
        self.ref_time_notz = datetime(1979, 1, 1, 0, 0, 0)

    def test_reftime_tzaware(self):
        with self.assertRaises(ValueError):
            # 'timestamps_reference_time' must be a timezone-aware datetime
            NWBFile('test session description',
                    'TEST124',
                    self.start_time,
                    timestamps_reference_time=self.ref_time_notz)
