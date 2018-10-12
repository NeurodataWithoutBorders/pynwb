import unittest
from pynwb import some_function


class DummyTestCase(unittest.TestCase):
    def test_some_function(self):
        arg = 'mouse'
        result = some_function(arg)

        self.assertEquals(result, arg)
