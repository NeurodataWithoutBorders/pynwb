''' Tests for NWBFile '''
import unittest
import six

from datetime import datetime

from pynwb import NWBFile
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
        expected_tags = tags1 + tags2
        self.nwbfile.create_epoch(source='a fake source', name='test_epoch1', start=0.0, stop=1.0,
                                  tags=tags1, descrition='test epoch')
        self.nwbfile.create_epoch(source='a fake source', name='test_epoch2', start=0.0, stop=1.0,
                                  tags=tags2, descrition='test epoch')
        tags = self.nwbfile.epoch_tags
        six.assertCountEqual(self, expected_tags, tags)
