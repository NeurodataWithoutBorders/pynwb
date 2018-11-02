import unittest2 as unittest

from pynwb.core import NWBContainer


class MyTestClass(NWBContainer):

    def __init__(self, name, parent=None):
        super(MyTestClass, self).__init__(name, parent=parent)

    def basic_add(self, **kwargs):
        return kwargs

    def basic_add2(self, **kwargs):
        return kwargs

    def basic_add2_kw(self, **kwargs):
        return kwargs


class MyTestSubclass(MyTestClass):

    def basic_add(self, **kwargs):
        return kwargs

    def basic_add2_kw(self, **kwargs):
        return kwargs


class TestNWBContainer(unittest.TestCase):

    def test_constructor(self):
        """Test that constructor properly sets parent
        """
        parent_obj = MyTestClass('obj1')
        child_obj = MyTestSubclass('obj2', parent=parent_obj)
        self.assertIs(child_obj.parent, parent_obj)

    def test_set_parent_parent(self):
        """Test that parent setter  properly sets parent
        """
        parent_obj = MyTestClass('obj1')
        child_obj = MyTestSubclass('obj2')
        child_obj.parent = parent_obj
        self.assertIs(child_obj.parent, parent_obj)


if __name__ == '__main__':
    unittest.main()
