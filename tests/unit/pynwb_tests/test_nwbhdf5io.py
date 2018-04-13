from pynwb import NWBHDF5IO, get_manager, validate

import unittest2 as unittest


class NWBHDF5IOTest(unittest.TestCase):

    def test_nwbhdf5io_without_path(self):
        with self.assertRaises(TypeError):
            NWBHDF5IO()

    def test_nwbhdf5io_with_empty_file(self):
        empty = 'tests/unit/pynwb_tests/data/empty.nwb'

        # TODO: Should this fail during initialization before
        # we call read()?
        with self.assertRaises(ValueError):
            NWBHDF5IO(path=empty).read()

    def test_nwbhdf5io_with_manager_and_extension(self):
        manager = get_manager()
        empty_nwb = 'tests/unit/pynwb_tests/data/empty.nwb'
        empty_extension = '/unit/pynwb_tests/data/empty.yaml'
        with self.assertRaises(ValueError):
            NWBHDF5IO(path=empty_nwb, extensions=empty_extension, manager=manager)

    def test_nwbhdf5io_validator_fail(self):
        empty_nwb = 'tests/unit/pynwb_tests/data/empty.nwb'
        nwb = NWBHDF5IO(path=empty_nwb)
        with self.assertRaises(ValueError):
            validate(io=nwb, namespace='core')
