import unittest
from .download_data import download_test_data
import pynwb


class ReadAPITestCase(unittest.TestCase):
    def setUp(self):
        read_test_path = 'tests/integration/test_read'
        self.read_test_path = read_test_path
        download_test_data()

    def test_read_ophys_example(self):
        path = '{}/data/ophys_example.nwb'.format(self.read_test_path)
        pynwb.NWBHDF5IO(path, mode='r').read()
