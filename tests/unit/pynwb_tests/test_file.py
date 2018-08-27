''' Tests for NWBFile '''
import unittest2 as unittest
import six
import numpy as np
import os

from datetime import datetime

from pynwb import NWBFile, TimeSeries
from pynwb import NWBHDF5IO
from pynwb.file import Subject
from pynwb.ecephys import ElectrodeTable


class NWBFileTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2017, 5, 1, 12, 0, 0)
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile('a fake source', 'a test session description for a test NWBFile',
                               'FILE123',
                               self.start,
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
                               data_collection='test data collection notes')

    def test_constructor(self):
        self.assertEqual(self.nwbfile.session_description, 'a test session description for a test NWBFile')
        self.assertEqual(self.nwbfile.identifier, 'FILE123')
        self.assertEqual(self.nwbfile.session_start_time, self.start)
        self.assertEqual(self.nwbfile.lab, 'a test lab')
        self.assertEqual(self.nwbfile.experimenter, 'A test experimenter')
        self.assertEqual(self.nwbfile.institution, 'a test institution')
        self.assertEqual(self.nwbfile.experiment_description, 'a test experiment description')
        self.assertEqual(self.nwbfile.session_id, 'test1')
        self.assertEqual(self.nwbfile.stimulus_notes, 'test stimulus notes')
        self.assertEqual(self.nwbfile.data_collection, 'test data collection notes')
        self.assertEqual(self.nwbfile.source_script, 'noscript')
        self.assertEqual(self.nwbfile.source_script_file_name, 'nofilename')

    def test_create_electrode_group(self):
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        d = self.nwbfile.create_device('a fake device', 'a fake source')
        elecgrp = self.nwbfile.create_electrode_group(name, 'a fake source', desc, loc, d)
        self.assertEqual(elecgrp.description, desc)
        self.assertEqual(elecgrp.location, loc)
        self.assertIs(elecgrp.device, d)

    def test_create_electrode_group_invalid_index(self):
        """
        Test the case where the user creates an electrode table region with
        indexes that are out of range of the amount of electrodes added.
        """
        nwbfile = NWBFile('a', 'b', 'c', datetime.now())
        device = nwbfile.create_device('a', 'b')
        elecgrp = nwbfile.create_electrode_group('a', 'b', 'c', device=device, location='a')
        for i in range(4):
            nwbfile.add_electrode(i, np.nan, np.nan, np.nan, np.nan, group=elecgrp,
                                  location='a', filtering='a', description='a')
        with self.assertRaises(IndexError) as err:
            nwbfile.create_electrode_table_region(list(range(6)), 'test')
        self.assertTrue('out of range' in str(err.exception))

    def test_epoch_tags(self):
        tags1 = ['t1', 't2']
        tags2 = ['t3', 't4']
        tstamps = np.arange(1.0, 100.0, 0.1, dtype=np.float)
        ts = TimeSeries("test_ts", "a hypothetical source", list(range(len(tstamps))), 'unit', timestamps=tstamps)
        expected_tags = tags1 + tags2
        self.nwbfile.create_epoch('a fake epoch', 0.0, 1.0, tags1, ts)
        self.nwbfile.create_epoch('a second fake epoch', 0.0, 1.0, tags2, ts)
        tags = self.nwbfile.epoch_tags
        six.assertCountEqual(self, expected_tags, tags)

    def test_add_acquisition(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.acquisition), 1)

    def test_add_stimulus(self):
        self.nwbfile.add_stimulus(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                             'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus), 1)

    def test_add_stimulus_template(self):
        self.nwbfile.add_stimulus_template(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                      'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.assertEqual(len(self.nwbfile.stimulus_template), 1)

    def test_add_acquisition_check_dups(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        with self.assertRaises(ValueError):
            self.nwbfile.add_acquisition(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                    'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))

    def test_get_acquisition_empty(self):
        with self.assertRaisesRegex(ValueError, "acquisition of NWBFile 'root' is empty"):
            self.nwbfile.get_acquisition()

    def test_get_acquisition_multiple_elements(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts1', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        self.nwbfile.add_acquisition(TimeSeries('test_ts2', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "more than one element in acquisition of NWBFile 'root' -- must specify a name"
        with self.assertRaisesRegex(ValueError,  msg):
            self.nwbfile.get_acquisition()

    def test_add_acquisition_invalid_name(self):
        self.nwbfile.add_acquisition(TimeSeries('test_ts', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                                                'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))
        msg = "'TEST_TS' not found in acquisition of NWBFile 'root'"
        with self.assertRaisesRegex(KeyError, msg):
            self.nwbfile.get_acquisition("TEST_TS")

    def test_set_electrode_table(self):
        table = ElectrodeTable('test_table')  # noqa: F405
        dev1 = self.nwbfile.create_device('dev1', 'a test source')  # noqa: F405
        group = self.nwbfile.create_electrode_group('tetrode1', 'a test source',
                                                    'tetrode description', 'tetrode location', dev1)
        table.add_row(1, 1.0, 2.0, 3.0, -1.0, 'CA1', 'none', 'first channel of tetrode', group)
        table.add_row(2, 1.0, 2.0, 3.0, -2.0, 'CA1', 'none', 'second channel of tetrode', group)
        table.add_row(3, 1.0, 2.0, 3.0, -3.0, 'CA1', 'none', 'third channel of tetrode', group)
        table.add_row(4, 1.0, 2.0, 3.0, -4.0, 'CA1', 'none', 'fourth channel of tetrode', group)
        self.nwbfile.set_electrode_table(table)
        self.assertIs(self.nwbfile.ec_electrodes, table)
        self.assertIs(table.parent, self.nwbfile)

    def test_add_unit_column(self):
        self.nwbfile.add_unit_column('unit_type', 'the type of unit')
        self.assertEqual(self.nwbfile.units.colnames, ('id', 'unit_type'))

    def test_add_unit(self):
        self.nwbfile.add_unit({'id': 1})
        self.assertEqual(len(self.nwbfile.units), 1)
        self.nwbfile.add_unit({'id': 2})
        self.nwbfile.add_unit({'id': 3})
        self.assertEqual(len(self.nwbfile.units), 3)

    def test_add_trial_column(self):
        self.nwbfile.add_trial_column('trial_type', 'the type of trial')
        self.assertEqual(self.nwbfile.trials.colnames, ('start', 'end', 'trial_type'))

    def test_add_trial(self):
        self.nwbfile.add_trial({'start': 10, 'end': 20})
        self.assertEqual(len(self.nwbfile.trials), 1)
        self.nwbfile.add_trial({'start': 30, 'end': 40})
        self.nwbfile.add_trial({'start': 50, 'end': 70})
        self.assertEqual(len(self.nwbfile.trials), 3)

    def test_add_electrode(self):
        dev1 = self.nwbfile.create_device('dev1', 'a test source')  # noqa: F405
        group = self.nwbfile.create_electrode_group('tetrode1', 'a test source',
                                                    'tetrode description', 'tetrode location', dev1)
        self.nwbfile.add_electrode(1, 1.0, 2.0, 3.0, -1.0, 'CA1', 'none', 'first channel of tetrode', group)
        self.assertEqual(self.nwbfile.ec_electrodes[0][0], 1)
        self.assertEqual(self.nwbfile.ec_electrodes[0][1], 1.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][2], 2.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][3], 3.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][4], -1.0)
        self.assertEqual(self.nwbfile.ec_electrodes[0][5], 'CA1')
        self.assertEqual(self.nwbfile.ec_electrodes[0][6], 'none')
        self.assertEqual(self.nwbfile.ec_electrodes[0][7], 'first channel of tetrode')
        self.assertEqual(self.nwbfile.ec_electrodes[0][8], group)

    def test_all_children(self):
        ts1 = TimeSeries('test_ts1', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ts2 = TimeSeries('test_ts2', 'unit test test_add_acquisition', [0, 1, 2, 3, 4, 5],
                         'grams', timestamps=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.nwbfile.add_acquisition(ts1)
        self.nwbfile.add_acquisition(ts2)
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        device = self.nwbfile.create_device('a fake device', 'a fake source')
        elecgrp = self.nwbfile.create_electrode_group(name, 'a fake source', desc, loc, device)
        children = self.nwbfile.all_children()
        self.assertIn(ts1, children)
        self.assertIn(ts2, children)
        self.assertIn(device, children)
        self.assertIn(elecgrp, children)

    def test_fail_if_source_script_file_name_without_source_script(self):
        with self.assertRaises(ValueError):
            # <-- source_script_file_name without source_script is not allowed
            NWBFile('a fake source', 'a test session description for a test NWBFile', 'FILE123', self.start,
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
                               weight='2 lbs',
                               source='Subject unittest')
        self.start = datetime(2017, 5, 1, 12, 0, 0)
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile('a fake source', 'a test session description for a test NWBFile',
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
        self.assertEqual(self.subject.source, 'Subject unittest')

    def test_nwbfile_constructor(self):
        self.assertIs(self.nwbfile.subject, self.subject)


class TestCacheSpec(unittest.TestCase):

    def setUp(self):
        self.path = 'unittest_cached_spec.nwb'

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_simple(self):
        nwbfile = NWBFile('source', ' ', ' ',
                          datetime.now(), datetime.now(),
                          institution='University of California, San Francisco',
                          lab='Chang Lab')
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile, cache_spec=True)
        reader = NWBHDF5IO(self.path, 'r', load_namespaces=True)
        nwbfile = reader.read()
