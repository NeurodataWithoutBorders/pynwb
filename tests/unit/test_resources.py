import warnings

from pynwb.resources import HERD
from pynwb.testing import TestCase


class TestNWBContainer(TestCase):
    def test_constructor(self):
        """
        Test constructor
        """
        with warnings.catch_warnings(record=True):
            warnings.filterwarnings(
                "ignore",
                message=r"HERD is experimental .*",
                category=UserWarning,
            )
            er = HERD()
            self.assertIsInstance(er, HERD)
