from pynwb.resources import ExternalResources
from pynwb.testing import TestCase


class TestNWBContainer(TestCase):
    def test_constructor(self):
        """
        Test constructor
        """
        er = ExternalResources()
        self.assertIsInstance(er, ExternalResources)
