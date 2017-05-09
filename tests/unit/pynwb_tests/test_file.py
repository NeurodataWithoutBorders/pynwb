''' Tests for NWBFile '''
import unittest

from datetime import datetime

from pynwb import NWBFile
from pynwb.ecephys import Device

class NWBFileTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2017, 5, 1, 12, 0, 0)
        self.path = 'nwbfile_test.h5'
        self.nwbfile = NWBFile(self.path, 'a test session description for a test NWBFile',
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
        ch_desc = [ 'the first channel', 'the second channel' ]
        ch_loc = [ 'area 1', 'area2' ]
        ch_filt = [ 'no filtering', 'no filtering' ]
        ch_coord = [ [1.0, 1.0, 1.0], [2.0, 2.0, 2.0] ]
        ch_imp = [-1, -1]
        desc = 'An example electrode'
        loc = 'an example location'
        d = Device('a fake device')
        elecgrp = self.nwbfile.create_electrode_group(name, ch_desc, ch_loc, ch_filt, ch_coord, ch_imp, desc, loc, d)
        self.assertEqual(elecgrp.channel_description, ch_desc)
        self.assertEqual(elecgrp.channel_coordinates, ch_coord)
        self.assertEqual(elecgrp.channel_filtering, ch_filt)
        self.assertEqual(elecgrp.channel_impedance, ch_imp)
        self.assertEqual(elecgrp.channel_location, ch_loc)
        self.assertEqual(elecgrp.description, desc)
        self.assertEqual(elecgrp.location, loc)
        self.assertIs(elecgrp.device, d)




