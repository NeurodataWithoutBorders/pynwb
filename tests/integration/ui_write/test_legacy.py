import os

import unittest2 as unittest

import pynwb


class TestLegacy(unittest.TestCase):

    def setUp(self):
        self.src_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '496908818s.nwb')
        self.filename = 'test_496908818s.nwb'
        raise unittest.SkipTest('Backwards compatibility not currently supported')

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_roundtrip(self):

        legacy_map = pynwb.legacy.get_type_map()
        io2 = pynwb.NWBHDF5IO(self.src_filename, extensions=legacy_map, mode='r')
        read_data = io2.read()

        io = pynwb.NWBHDF5IO(self.filename, mode='w')
        io.write(read_data)
        io.close()
        io2.close()
