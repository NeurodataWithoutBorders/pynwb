import unittest
import subprocess

import pynwb


class ReadLegacyTestCase(unittest.TestCase):
    def setUp(self):
        read_test_path = 'tests/integration/test_read'
        self.read_test_path = read_test_path
        subprocess.call(['./{}/download_data.sh'.format(read_test_path)])

    def test_read_ophys_example(self):
        path = '{}/data/ophys_example.nwb'.format(self.read_test_path)
        pynwb.NWBHDF5IO(path, mode='r').read()

    def test_read_legacy_extension(self):
        legacy_map = pynwb.legacy.get_type_map()
        path = '{}/data/570014520.nwb'.format(self.read_test_path)
        pynwb.NWBHDF5IO(path, extensions=legacy_map, mode='r').read()
