from pynwb.resources import HERD
from pynwb.testing import TestCase


class TestNWBContainer(TestCase):
    def test_constructor(self):
        """
        Test constructor
        """
        er = HERD()
        self.assertIsInstance(er, HERD)
