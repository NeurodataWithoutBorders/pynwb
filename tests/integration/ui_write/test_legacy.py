import os
import unittest

from pynwb import NWBHDF5IO
from pynwb.testing import TestCase
import pynwb.legacy


class TestLegacy(TestCase):

    def setUp(self):
        self.src_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '496908818s.nwb')
        self.filename = 'test_496908818s.nwb'
        raise unittest.SkipTest('Backwards compatibility not currently supported')

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_roundtrip(self):
        legacy_map = pynwb.legacy.get_type_map()
        with NWBHDF5IO(self.src_filename, extensions=legacy_map, mode='r') as io2:
            read_data = io2.read()

            with NWBHDF5IO(self.filename, mode='w') as io:
                io.write(read_data)
