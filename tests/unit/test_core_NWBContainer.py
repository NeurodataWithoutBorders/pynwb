import unittest

from pynwb.core import NWBContainer
from hdmf.utils import docval


class MyTestClass(NWBContainer):

    __nwbfields__ = ('prop1', 'prop2')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this container'})
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prop1 = 'test1'


class TestNWBContainer(unittest.TestCase):

    def test_constructor(self):
        """Test constructor
        """
        obj = MyTestClass('obj1')
        self.assertEqual(obj.name, 'obj1')
        obj.prop2 = 'test2'

    def test_nwbfields(self):
        """Test that getters and setters work for nwbfields
        """
        obj = MyTestClass('obj1')
        obj.prop2 = 'test2'
        self.assertEqual(obj.prop1, 'test1')
        self.assertEqual(obj.prop2, 'test2')


if __name__ == '__main__':
    unittest.main()
