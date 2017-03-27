import unittest

from pynwb.spec import GroupSpec, AttributeSpec, DatasetSpec
from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.core import NWBContainer
from pynwb.spec.spec import SpecCatalog
from pynwb.io.build.map import ObjectMapper, BuildManager, TypeMap

class MyNWBContainer(NWBContainer):
    def __init__(self, data, attr1, attr2, attr3=3.14):
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
        self.build_manager = BuildManager()
        my_spec = GroupSpec('A test group specification with a neurodata type',
                         neurodata_type_def='MyNWBContainer',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute'),
                                     AttributeSpec('attr2', 'int', 'an example integer attribute')])
        self.type_map.register_spec(MyNWBContainer, my_spec)

    def test_default_mapping(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        builder = self.type_map.build(container_inst, self.build_manager)
        expected = GroupBuilder(datasets={'data': DatasetBuilder(list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10})

        self.assertDictEqual(builder, expected)

class TestNested(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.build_manager = BuildManager()
        my_spec = GroupSpec('A test group specification with a neurodata type',
                         neurodata_type_def='MyNWBContainer',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data', attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(MyNWBContainer, my_spec)

    def test_register(self):

        @self.type_map.neurodata_type('MyNWBContainer')
        class MyNWBContainerMap(ObjectMapper):
            def __init__(self, spec):
                super(MyNWBContainerMap, self).__init__(spec)
                #super().__init__(spec)
                #attr2_spec = spec.get_dataset('data').get_attribute('attr2')
                #self.map_attr('attr2', attr2_spec)

        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        cls = self.type_map.get_map(container_inst)
        self.assertIsInstance(cls, MyNWBContainerMap)

    def test_override(self):
        container_inst = MyNWBContainer(list(range(10)), 'value1', 10)
        expected = GroupBuilder(datasets={'data': DatasetBuilder(list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder = self.type_map.build(container_inst, self.build_manager)
        self.assertDictEqual(builder, expected)
