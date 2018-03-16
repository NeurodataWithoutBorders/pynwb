''' Tests for NWBFile '''
import unittest
import six
import numpy as np

from datetime import datetime

from pynwb import NWBFile, TimeSeries
from pynwb.file import Subject
from pynwb.ecephys import Device


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
                               session_id='test1')

    def test_constructor(self):
        self.assertEqual(self.nwbfile.session_description, 'a test session description for a test NWBFile')
        self.assertEqual(self.nwbfile.identifier, 'FILE123')
        self.assertEqual(self.nwbfile.session_start_time, self.start)
        self.assertEqual(self.nwbfile.lab, 'a test lab')
        self.assertEqual(self.nwbfile.experimenter, 'A test experimenter')
        self.assertEqual(self.nwbfile.institution, 'a test institution')
        self.assertEqual(self.nwbfile.experiment_description, 'a test experiment description')
        self.assertEqual(self.nwbfile.session_id, 'test1')

    def test_create_electrode_group(self):
        name = 'example_electrode_group'
        desc = 'An example electrode'
        loc = 'an example location'
        d = Device('a fake device', 'a fake source')
        elecgrp = self.nwbfile.create_electrode_group(name, 'a fake source', desc, loc, d)
        self.assertEqual(elecgrp.description, desc)
        self.assertEqual(elecgrp.location, loc)
        self.assertIs(elecgrp.device, d)

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
