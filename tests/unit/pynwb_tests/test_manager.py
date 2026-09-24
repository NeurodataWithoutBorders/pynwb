from pynwb import get_manager
from pynwb.form.build import TypeMap
from pynwb.form.spec import NamespaceCatalog

import unittest2 as unittest


class ManagerTest(unittest.TestCase):

    def test_manager_with_non_path_extension(self):
        with self.assertRaises(IOError):
            get_manager(extensions='foobar')

    def test_manager_with_empty_file(self):
        empty = 'tests/unit/pynwb_tests/data/empty.yaml'
        with self.assertRaises(AttributeError):
            get_manager(extensions=empty)

    def test_manager_core_namespace(self):
        manager = get_manager()
        self.assertIn('core', manager.namespace_catalog.namespaces)

    def test_manager_with_real_namespace(self):
        extension = 'tests/unit/pynwb_tests/data/crcnsret1.namespace.yaml'
        manager = get_manager(extensions=extension)
        self.assertIn('crcnsret1', manager.namespace_catalog.namespaces)

    def test_manager_with_type_map(self):
        namespace_catalog = NamespaceCatalog()
        type_map = TypeMap(namespace_catalog)
        manager = get_manager(extensions=type_map)
        self.assertEquals(0, len(manager.namespace_catalog.namespaces))

    def test_manager_with_empty_list(self):
        manager = get_manager(extensions=[])
        self.assertIn('core', manager.namespace_catalog.namespaces)

    def test_manager_with_dummy_list(self):
        with self.assertRaises(IOError):
            get_manager(extensions=['foo', 'bar'])

    def test_manager_with_same_namespace_list(self):
        extension = 'tests/unit/pynwb_tests/data/crcnsret1.namespace.yaml'
        manager = get_manager(extensions=[extension, extension])
        namespaces = manager.namespace_catalog.namespaces
        # Make sure extension is registered only once
        self.assertEquals(len(set(namespaces)), len(namespaces))

    def test_manager_with_wrong_type_list_items(self):
        extensions = [1, 2, 3]
        with self.assertRaises(ValueError):
            get_manager(extensions=extensions)

    def test_manager_with_list_of_type_maps(self):
        namespace_catalog = NamespaceCatalog()
        type_map = TypeMap(namespace_catalog)
        type_map_2 = TypeMap(namespace_catalog)
        manager = get_manager(extensions=[type_map, type_map_2])
        self.assertIn('core', manager.namespace_catalog.namespaces)

    def test_manager_with_list_of_type_map_and_path(self):
        namespace_catalog = NamespaceCatalog()
        type_map = TypeMap(namespace_catalog)
        extension = 'tests/unit/pynwb_tests/data/crcnsret1.namespace.yaml'
        manager = get_manager(extensions=[type_map, extension])
        self.assertIn('crcnsret1', manager.namespace_catalog.namespaces)
        self.assertIn('core', manager.namespace_catalog.namespaces)
