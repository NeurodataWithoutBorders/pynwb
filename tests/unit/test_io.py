import unittest

from pynwb.spec import GroupSpec, AttributeSpec, DatasetSpec
from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.core import NWBContainer, docval, getargs
from pynwb.spec.spec import SpecCatalog
from pynwb.io.build.map import ObjectMapper, BuildManager, TypeMap

class MyNWBContainer(NWBContainer):

    @docval({'name': 'data', 'type': list, 'doc': 'some data'},
            {'name': 'attr1', 'type': str, 'doc': 'an attribute'},
            {'name': 'attr2', 'type': int, 'doc': 'another attribute'},
            {'name': 'attr3', 'type': float, 'doc': 'a third attribute', 'default': 3.14})
    def __init__(self, **kwargs):
        data, attr1, attr2, attr3 = getargs('data', 'attr1', 'attr2', 'attr3', kwargs)
        super(MyNWBContainer, self).__init__()
        self.__data = data
        self.__attr1 = attr1
        self.__attr2 = attr2
        self.__attr3 = attr3

    @property
    def data(self):
        return self.__data

    @property
    def attr1(self):
        return self.__attr1

    @property
    def attr2(self):
        return self.__attr2

    @property
    def attr3(self):
        return self.__attr3


class TestUnNested(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.build_manager = BuildManager(self.type_map)
        self.my_spec = GroupSpec('A test group specification with a neurodata type',
                         name="my_container",
                         neurodata_type_def='MyNWBContainer',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute'),
                                     AttributeSpec('attr2', 'int', 'an example integer attribute')])
        self.type_map.register_spec(MyNWBContainer, self.my_spec)

    def test_get_map(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIsInstance(mapper, ObjectMapper)
        self.assertIs(mapper.spec, self.my_spec)

    def test_register(self):
        @self.type_map.neurodata_type('MyNWBContainer')
        class MyMap(ObjectMapper):
            pass
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIs(mapper.spec, self.my_spec)
        self.assertIsInstance(mapper, MyMap)


    def test_default_mapping(self):
        ''' Test default mapping functionality '''
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        builder = self.type_map.build(container_inst, self.build_manager)
        expected = GroupBuilder('my_container', datasets={'data': DatasetBuilder('data', list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10})
        self.assertDictEqual(builder, expected)

class TestNested(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.my_spec = GroupSpec('A test group specification with a neurodata type',
                                 name="my_container",
                                 neurodata_type_def='MyNWBContainer',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data', attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(MyNWBContainer, self.my_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_container', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder = self.type_map.build(container_inst, self.build_manager)
        self.assertDictEqual(builder, expected)

class TestBuildManager(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.my_spec = GroupSpec('A test group specification with a neurodata type',
                                 name="my_container",
                                 neurodata_type_def='MyNWBContainer',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data', attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(MyNWBContainer, self.my_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_container', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder1 = self.build_manager.build(container_inst)
        self.assertDictEqual(builder1, expected)

    def test_memoization(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_container', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder1 = self.build_manager.build(container_inst)
        builder2 = self.build_manager.build(container_inst)
        self.assertDictEqual(builder1, expected)
        self.assertIs(builder1, builder2)


#TODO:
class TestWildCardNamedSpecs(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
