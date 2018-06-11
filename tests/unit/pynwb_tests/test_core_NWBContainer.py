import unittest2 as unittest

from pynwb.core import NWBContainer


class MyTestClass(NWBContainer):

    def __init__(self, src, name, parent=None):
        super(MyTestClass, self).__init__(src, name, parent=parent)

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
        parent_obj = MyTestClass('test source', 'obj1')
        child_obj = MyTestSubclass('test source', 'obj2', parent=parent_obj)
        self.assertIs(child_obj.parent, parent_obj)

    def test_set_parent_parent(self):
        """Test that parent setter  properly sets parent
        """
        parent_obj = MyTestClass('test source', 'obj1')
        child_obj = MyTestSubclass('test source', 'obj2')
        child_obj.parent = parent_obj
        self.assertIs(child_obj.parent, parent_obj)

    def test_subtypes_api(self):
        """Test the subtypes method for getting all subtypes of a class"""
        subs = NWBContainer.subtypes()

        def all_subs(myclass):
            return set(myclass.__subclasses__()).union( [s for c in myclass.__subclasses__() for s in all_subs(c)])

        expected_subs = all_subs(NWBContainer)
        self.assertSetEqual(subs, expected_subs)


if __name__ == '__main__':
    unittest.main()
