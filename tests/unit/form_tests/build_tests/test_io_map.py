import unittest2 as unittest

from pynwb.form.spec import GroupSpec, AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace, NamespaceCatalog
from pynwb.form.build import GroupBuilder, DatasetBuilder, ObjectMapper, BuildManager, TypeMap
from pynwb.form import Container
from pynwb.form.utils import docval, getargs, get_docval

from abc import ABCMeta
from six import with_metaclass

CORE_NAMESPACE = 'test_core'


class Bar(Container):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this Bar'},
            {'name': 'data', 'type': list, 'doc': 'some data'},
            {'name': 'attr1', 'type': str, 'doc': 'an attribute'},
            {'name': 'attr2', 'type': int, 'doc': 'another attribute'},
            {'name': 'attr3', 'type': float, 'doc': 'a third attribute', 'default': 3.14})
    def __init__(self, **kwargs):
        name, data, attr1, attr2, attr3 = getargs('name', 'data', 'attr1', 'attr2', 'attr3', kwargs)
        super(Bar, self).__init__(name=name)
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


class Foo(Container):
    pass


class TestGetSubSpec(unittest.TestCase):

    def setUp(self):
        self.bar_spec = GroupSpec('A test group specification with a data type', data_type_def='Bar')
        spec_catalog = SpecCatalog()
        spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=spec_catalog)
        namespace_catalog = NamespaceCatalog()
        namespace_catalog.add_namespace(CORE_NAMESPACE, namespace)
        self.type_map = TypeMap(namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)

    def test_get_subspec_data_type_noname(self):
        parent_spec = GroupSpec('Something to hold a Bar', 'bar_bucket', groups=[self.bar_spec])
        sub_builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar', 'namespace': CORE_NAMESPACE})
        builder = GroupBuilder('bar_bucket', groups={'my_bar': sub_builder})  # noqa: F841
        result = self.type_map.get_subspec(parent_spec, sub_builder)
        self.assertIs(result, self.bar_spec)

    def test_get_subspec_named(self):
        child_spec = GroupSpec('A test group specification with a data type', 'my_subgroup')
        parent_spec = GroupSpec('Something to hold a Bar', 'my_group', groups=[child_spec])
        sub_builder = GroupBuilder('my_subgroup', attributes={'data_type': 'Bar', 'namespace': CORE_NAMESPACE})
        builder = GroupBuilder('my_group', groups={'my_bar': sub_builder})  # noqa: F841
        result = self.type_map.get_subspec(parent_spec, sub_builder)
        self.assertIs(result, child_spec)


class TestTypeMap(unittest.TestCase):

    def setUp(self):
        self.bar_spec = GroupSpec('A test group specification with a data type', data_type_def='Bar')
        self.foo_spec = GroupSpec('A test group specification with data type Foo', data_type_def='Foo')
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.spec_catalog.register_spec(self.foo_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}],
                                       catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog()
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Foo', Foo)
        # self.build_manager = BuildManager(self.type_map)

    def test_get_map_unique_mappers(self):
        self.type_map.register_map(Bar, ObjectMapper)
        self.type_map.register_map(Foo, ObjectMapper)
        bar_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        foo_inst = Foo(name='my_foo')
        bar_mapper = self.type_map.get_map(bar_inst)
        foo_mapper = self.type_map.get_map(foo_inst)
        self.assertIsNot(bar_mapper, foo_mapper)

    def test_get_map(self):
        self.type_map.register_map(Bar, ObjectMapper)
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIsInstance(mapper, ObjectMapper)
        self.assertIs(mapper.spec, self.bar_spec)
        mapper2 = self.type_map.get_map(container_inst)
        self.assertIs(mapper, mapper2)

    def test_get_map_register(self):
        class MyMap(ObjectMapper):
            pass
        self.type_map.register_map(Bar, MyMap)

        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIs(mapper.spec, self.bar_spec)
        self.assertIsInstance(mapper, MyMap)


class TestDynamicContainer(unittest.TestCase):

    def setUp(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                                  data_type_def='Bar',
                                  datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                        attributes=[AttributeSpec(
                                                            'attr2', 'an example integer attribute', 'int')])],
                                  attributes=[AttributeSpec('attr1', 'an example string attribute', 'text')])
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE,
                                       [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog()
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)
        self.type_map.register_map(Bar, ObjectMapper)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.bar_spec)

    def test_dynamic_container_creation(self):
        baz_spec = GroupSpec('A test extension with no Container class',
                             data_type_def='Baz', data_type_inc=self.bar_spec,
                             attributes=[AttributeSpec('attr3', 'an example float attribute', 'float'),
                                         AttributeSpec('attr4', 'another example float attribute', 'float')])
        self.spec_catalog.register_spec(baz_spec, 'extension.yaml')
        cls = self.type_map.get_container_cls(CORE_NAMESPACE, 'Baz')
        expected_args = {'name', 'data', 'attr1', 'attr2', 'attr3', 'attr4'}
        received_args = set()
        for x in get_docval(cls.__init__):
            received_args.add(x['name'])
            with self.subTest(name=x['name']):
                self.assertNotIn('default', x)
        self.assertSetEqual(expected_args, received_args)
        self.assertEqual(cls.__name__, 'Baz')
        self.assertTrue(issubclass(cls, Bar))

    def test_dynamic_container_creation_defaults(self):
        baz_spec = GroupSpec('A test extension with no Container class',
                             data_type_def='Baz', data_type_inc=self.bar_spec,
                             attributes=[AttributeSpec('attr3', 'an example float attribute', 'float'),
                                         AttributeSpec('attr4', 'another example float attribute', 'float')])
        self.spec_catalog.register_spec(baz_spec, 'extension.yaml')
        cls = self.type_map.get_container_cls(CORE_NAMESPACE, 'Baz')
        expected_args = {'name', 'data', 'attr1', 'attr2', 'attr3', 'attr4'}
        received_args = set(map(lambda x: x['name'], get_docval(cls.__init__)))
        self.assertSetEqual(expected_args, received_args)
        self.assertEqual(cls.__name__, 'Baz')
        self.assertTrue(issubclass(cls, Bar))

    def test_dynamic_container_constructor(self):
        baz_spec = GroupSpec('A test extension with no Container class',
                             data_type_def='Baz', data_type_inc=self.bar_spec,
                             attributes=[AttributeSpec('attr3', 'an example float attribute', 'float'),
                                         AttributeSpec('attr4', 'another example float attribute', 'float')])
        self.spec_catalog.register_spec(baz_spec, 'extension.yaml')
        cls = self.type_map.get_container_cls(CORE_NAMESPACE, 'Baz')
        # TODO: test that constructor works!
        inst = cls('My Baz', [1, 2, 3, 4], 'string attribute', 1000, attr3=98.6, attr4=1.0)
        self.assertEqual(inst.name, 'My Baz')
        self.assertEqual(inst.data, [1, 2, 3, 4])
        self.assertEqual(inst.attr1, 'string attribute')
        self.assertEqual(inst.attr2, 1000)
        self.assertEqual(inst.attr3, 98.6)
        self.assertEqual(inst.attr4, 1.0)


class TestObjectMapper(with_metaclass(ABCMeta, unittest.TestCase)):

    def setUp(self):
        self.setUpBarSpec()
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE,
                                       [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog()
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Bar', Bar)
        self.type_map.register_map(Bar, ObjectMapper)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.bar_spec)

    def setUpBarSpec(self):
        raise unittest.SkipTest('setUpBarSpec not implemented')

    def test_default_mapping(self):
        attr_map = self.mapper.get_attr_names(self.bar_spec)
        keys = set(attr_map.keys())
        for key in keys:
            with self.subTest(key=key):
                self.assertIs(attr_map[key], self.mapper.get_attr_spec(key))
                self.assertIs(attr_map[key], self.mapper.get_carg_spec(key))


class TestObjectMapperNested(TestObjectMapper):

    def setUpBarSpec(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                                  data_type_def='Bar',
                                  datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                        attributes=[AttributeSpec(
                                                            'attr2', 'an example integer attribute', 'int')])],
                                  attributes=[AttributeSpec('attr1', 'an example string attribute', 'text')])

    def test_build(self):
        ''' Test default mapping functionality when object attributes map to an  attribute deeper
        than top-level Builder '''
        container_inst = Bar('my_bar', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder(
            'data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1'})
        builder = self.mapper.build(container_inst, self.manager)
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        ''' Test default mapping functionality when object attributes map to an attribute
        deeper than top-level Builder '''
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder(
            'data', list(range(10)), attributes={'attr2': 10})},
                               attributes={'attr1': 'value1', 'data_type': 'Bar', 'namespace': CORE_NAMESPACE})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

    def test_default_mapping_keys(self):
        attr_map = self.mapper.get_attr_names(self.bar_spec)
        keys = set(attr_map.keys())
        expected = {'attr1', 'data', 'attr2'}
        self.assertSetEqual(keys, expected)


class TestObjectMapperNoNesting(TestObjectMapper):

    def setUpBarSpec(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                                  data_type_def='Bar',
                                  datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                                  attributes=[AttributeSpec('attr1', 'an example string attribute', 'text'),
                                              AttributeSpec('attr2', 'an example integer attribute', 'int')])

    def test_build(self):
        ''' Test default mapping functionality when no attributes are nested '''
        container = Bar('my_bar', list(range(10)), 'value1', 10)
        builder = self.mapper.build(container, self.manager)
        expected = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10})
        self.assertDictEqual(builder, expected)

    def test_construct(self):
        builder = GroupBuilder('my_bar', datasets={'data': DatasetBuilder('data', list(range(10)))},
                               attributes={'attr1': 'value1', 'attr2': 10, 'data_type': 'Bar',
                                           'namespace': CORE_NAMESPACE})
        expected = Bar('my_bar', list(range(10)), 'value1', 10)
        container = self.mapper.construct(builder, self.manager)
        self.assertEqual(container, expected)

    def test_default_mapping_keys(self):
        attr_map = self.mapper.get_attr_names(self.bar_spec)
        keys = set(attr_map.keys())
        expected = {'attr1', 'data', 'attr2'}
        self.assertSetEqual(keys, expected)


class TestObjectMapperContainer(TestObjectMapper):

    def setUpBarSpec(self):
        self.bar_spec = GroupSpec('A test group specification with a data type',
                                  data_type_def='Bar',
                                  groups=[GroupSpec('an example group', data_type_def='Foo')],
                                  attributes=[AttributeSpec('attr1', 'an example string attribute', 'text'),
                                              AttributeSpec('attr2', 'an example integer attribute', 'int')])

    def test_default_mapping_keys(self):
        attr_map = self.mapper.get_attr_names(self.bar_spec)
        keys = set(attr_map.keys())
        expected = {'attr1', 'foo', 'attr2'}
        self.assertSetEqual(keys, expected)


if __name__ == '__main__':
    unittest.main()
