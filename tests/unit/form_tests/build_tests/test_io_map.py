import unittest

from form.spec import GroupSpec, AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace, NamespaceCatalog
from form.build import GroupBuilder, DatasetBuilder, ObjectMapper, BuildManager, TypeMap, get_subspec
from form import Container
from form.utils import docval, getargs

CORE_NAMESPACE = 'core'

class Bar(Container):

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
    def data_type(self):
        return 'Bar'

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

    def test_get_subspec_data_type_noname(self):
        child_spec = GroupSpec('A test group specification with a data type', data_type_def='Bar')
        parent_spec = GroupSpec('Something to hold a Bar', 'bar_bucket', groups=[child_spec])
        sub_builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar'})
        builder = GroupBuilder('bar_bucket', groups={'my_bar': sub_builder})
        result = get_subspec(parent_spec, sub_builder)
        self.assertIs(result, child_spec)

    def test_get_subspec_named(self):
        child_spec = GroupSpec('A test group specification with a data type', 'my_subgroup')
        parent_spec = GroupSpec('Something to hold a Bar', 'my_group', groups=[child_spec])
        sub_builder = GroupBuilder('my_subgroup', attributes={'data_type': 'Bar'})
        builder = GroupBuilder('my_group', groups={'my_bar': sub_builder})
        result = get_subspec(parent_spec, sub_builder)
        self.assertIs(result, child_spec)

class TestTypeMap(unittest.TestCase):

    def setUp(self):
        self.bar_spec = GroupSpec('A test group specification with a data type', data_type_def='Bar')
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog(CORE_NAMESPACE)
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)
        #self.build_manager = BuildManager(self.type_map)

    def test_get_map(self):
        self.type_map.register_map(Bar, ObjectMapper)
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIsInstance(mapper, ObjectMapper)
        self.assertIs(mapper.spec, self.bar_spec)

    def test_get_map_register(self):
        class MyMap(ObjectMapper):
            pass
        self.type_map.register_map(Bar, MyMap)

        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIs(mapper.spec, self.bar_spec)
        self.assertIsInstance(mapper, MyMap)

class TestObjectMapper(unittest.TestCase):

    def setUp(self):
        self.setUpBarSpec()
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog(CORE_NAMESPACE)
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)
        self.type_map.register_map(Bar, ObjectMapper)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.bar_spec)

    def setUpBarSpec(self):
        raise SkipTest('setUpBarSpec not implemented')

class TestObjectMapperNested(TestObjectMapper):

    def setUpBarSpec(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                                 data_type_def='Bar',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])

    def test_build(self):
        ''' Test default mapping functionality when object attributes map to an attribute deeper than top-level Builder '''
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder = self.mapper.build(container_inst, self.manager)
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        ''' Test default mapping functionality when object attributes map to an attribute deeper than top-level Builder '''
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'data_type': 'Bar'})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

#class TestObjectMapperNoNesting(unittest.TestCase):
class TestObjectMapperNoNesting(TestObjectMapper):

    def setUpBarSpec(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                         data_type_def='Bar',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute'),
                                     AttributeSpec('attr2', 'int', 'an example integer attribute')])


    def test_build(self):
        ''' Test default mapping functionality when no attributes are nested '''
        container = Bar('my_bar', list(range(10)), 'value1', 10)
        builder = self.mapper.build(container, self.manager)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10})
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                               attributes={'attr1': 'value1', 'attr2': 10, 'data_type': 'Bar'})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

if __name__ == '__main__':
    unittest.main()
