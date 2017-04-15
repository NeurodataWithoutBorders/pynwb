import unittest

from pynwb.spec import GroupSpec, AttributeSpec, DatasetSpec
from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.core import NWBContainer, docval, getargs
from pynwb.spec.spec import SpecCatalog
from pynwb.io.build.map import ObjectMapper, BuildManager, TypeMap, get_subspec

class Bar(NWBContainer):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this Bar'},
            {'name': 'data', 'type': list, 'doc': 'some data'},
            {'name': 'attr1', 'type': str, 'doc': 'an attribute'},
            {'name': 'attr2', 'type': int, 'doc': 'another attribute'},
            {'name': 'attr3', 'type': float, 'doc': 'a third attribute', 'default': 3.14})
    def __init__(self, **kwargs):
        name, data, attr1, attr2, attr3 = getargs('name', 'data', 'attr1', 'attr2', 'attr3', kwargs)
        super(Bar, self).__init__()
        self.__name = name
        self.__data = data
        self.__attr1 = attr1
        self.__attr2 = attr2
        self.__attr3 = attr3

    def __eq__(self, other):
        attrs = ('name', 'data', 'attr1', 'attr2', 'attr3')
        return all(getattr(self, a) == getattr(other, a) for a in attrs)

    def __str__(self):
        attrs = ('name', 'data', 'attr1', 'attr2', 'attr3')
        return ','.join('%s=%s' % (a, getattr(self, a)) for a in attrs)

    @property
    def name(self):
        return self.__name

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

class TestGetSubSpec(unittest.TestCase):

    def test_get_subspec_neurodata_type_noname(self):
        child_spec = GroupSpec('A test group specification with a neurodata type', neurodata_type_def='Bar')
        parent_spec = GroupSpec('Something to hold a Bar', 'bar_bucket', groups=[child_spec])
        sub_builder = GroupBuilder('my_bar', attributes={'neurodata_type': 'Bar'})
        builder = GroupBuilder('bar_bucket', groups={'my_bar': sub_builder})
        result = get_subspec(parent_spec, sub_builder)
        self.assertIs(result, child_spec)

    def test_get_subspec_named(self):
        child_spec = GroupSpec('A test group specification with a neurodata type', 'my_subgroup')
        parent_spec = GroupSpec('Something to hold a Bar', 'my_group', groups=[child_spec])
        sub_builder = GroupBuilder('my_subgroup', attributes={'neurodata_type': 'Bar'})
        builder = GroupBuilder('my_group', groups={'my_bar': sub_builder})
        result = get_subspec(parent_spec, sub_builder)
        self.assertIs(result, child_spec)

class TestTypeMap(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.build_manager = BuildManager(self.type_map)

    def test_get_map(self):
        bar_spec = GroupSpec('A test group specification with a neurodata type', neurodata_type_def='Bar')
        self.type_map.register_spec(Bar, bar_spec)
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIsInstance(mapper, ObjectMapper)
        self.assertIs(mapper.spec, bar_spec)

    def test_get_map_register(self):
        bar_spec = GroupSpec('A test group specification with a neurodata type', neurodata_type_def='Bar')
        self.type_map.register_spec(Bar, bar_spec)
        @self.type_map.neurodata_type('Bar')
        class MyMap(ObjectMapper):
            pass
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIs(mapper.spec, bar_spec)
        self.assertIsInstance(mapper, MyMap)

class TestObjectMapperNested(unittest.TestCase):

    def setUp(self):
        self.type_map = TypeMap(SpecCatalog())
        self.bar_spec = GroupSpec('A test group specification with a neurodata type',
                                 neurodata_type_def='Bar',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(Bar, self.bar_spec)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.bar_spec)

    def test_build(self):
        ''' Test default mapping functionality when object attributes map to an attribute deeper than top-level Builder '''
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Bar'})
        builder = self.mapper.build(container_inst, self.manager)
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        ''' Test default mapping functionality when object attributes map to an attribute deeper than top-level Builder '''
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Bar'})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

class TestObjectMapperNoNesting(unittest.TestCase):

    def setUp(self):
        self.type_map = TypeMap(SpecCatalog())
        self.bar_spec = GroupSpec('A test group specification with a neurodata type',
                         neurodata_type_def='Bar',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute'),
                                     AttributeSpec('attr2', 'int', 'an example integer attribute')])
        self.type_map.register_spec(Bar, self.bar_spec)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.bar_spec)

    def test_build(self):
        ''' Test default mapping functionality when no attributes are nested '''
        container = Bar('my_bar', list(range(10)), 'value1', 10)
        builder = self.mapper.build(container, self.manager)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10, 'neurodata_type': 'Bar'})
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                               attributes={'attr1': 'value1', 'attr2': 10, 'neurodata_type': 'Bar'})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

if __name__ == '__main__':
    unittest.main()
