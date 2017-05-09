''' Tests for NWBFile '''
import unittest

from datetime import datetime

from pynwb import NWBFile
from pynwb.ecephys import ElectrodeGroup, ElectricalSeries

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





