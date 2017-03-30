import unittest

from pynwb.core import NWBContainer

class MyTestClass(NWBContainer):

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
           and subcontainers called with parent
        """
        parent_obj = MyTestClass()
        child_obj = MyTestSubclass(parent=parent_obj)
        self.assertIs(child_obj.parent, parent_obj)

    def test_set_parent_parent(self):
        """Test that parent setter  properly sets parent
        """
        parent_obj = MyTestClass()
        child_obj = MyTestSubclass()
        child_obj.parent = parent_obj
        self.assertIs(child_obj.parent, parent_obj)

    def test_set_parent_subcontainer(self):
        """Test that parent setter properly sets parent subcontainers
        """
        parent_obj = MyTestClass()
        child_obj = MyTestSubclass()
        child_obj.parent = parent_obj
        self.assertListEqual(parent_obj.subcontainers, [child_obj])


if __name__ == '__main__':
    unittest.main()