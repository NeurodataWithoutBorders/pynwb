import datadiff
import unittest
import json
import sys

from pynwb.spec import GroupSpec, AttributeSpec, DatasetSpec
from pynwb.io.build.builders import GroupBuilder, DatasetBuilder
from pynwb.core import NWBContainer, docval, getargs
from pynwb.spec.spec import SpecCatalog
from pynwb.io.build.map import ObjectMapper, BuildManager, TypeMap

class Foo(NWBContainer):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this Foo'},
            {'name': 'data', 'type': list, 'doc': 'some data'},
            {'name': 'attr1', 'type': str, 'doc': 'an attribute'},
            {'name': 'attr2', 'type': int, 'doc': 'another attribute'},
            {'name': 'attr3', 'type': float, 'doc': 'a third attribute', 'default': 3.14})
    def __init__(self, **kwargs):
        name, data, attr1, attr2, attr3 = getargs('name', 'data', 'attr1', 'attr2', 'attr3', kwargs)
        super(Foo, self).__init__()
        self.__name = name
        self.__data = data
        self.__attr1 = attr1
        self.__attr2 = attr2
        self.__attr3 = attr3

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

class FooBucket(NWBContainer):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this bucket'},
            {'name': 'foos', 'type': list, 'doc': 'the Foo objects in this bucket', 'default': list()})
    def __init__(self, **kwargs):
        name, foos = getargs('name', 'foos', kwargs)
        super(FooBucket, self).__init__()
        self.__name = name
        self.__foos = foos

    @property
    def name(self):
        return self.__name

    @property
    def foos(self):
        return self.__foos

    def add_foo(self, foo):
        self.__foos.append(foo)


class TestTypeMap(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.build_manager = BuildManager(self.type_map)
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                         neurodata_type_def='Foo',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data')],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute'),
                                     AttributeSpec('attr2', 'int', 'an example integer attribute')])
        self.type_map.register_spec(Foo, self.foo_spec)

    def test_get_map(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIsInstance(mapper, ObjectMapper)
        self.assertIs(mapper.spec, self.foo_spec)

    def test_get_map_register(self):
        @self.type_map.neurodata_type('Foo')
        class MyMap(ObjectMapper):
            pass
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        mapper = self.type_map.get_map(container_inst)
        self.assertIs(mapper.spec, self.foo_spec)
        self.assertIsInstance(mapper, MyMap)


    def test_build_default_mapping(self):
        ''' Test default mapping functionality '''
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        builder = self.type_map.build(container_inst, self.build_manager)
        expected = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)))},
                                attributes={'attr1': 'value1', 'attr2': 10, 'neurodata_type': 'Foo'})
        self.assertDictEqual(builder, expected)

class TestNested(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                                 neurodata_type_def='Foo',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data', attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(Foo, self.foo_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        builder = self.type_map.build(container_inst, self.build_manager)
        self.assertDictEqual(builder, expected)

class TestBuildManagerBuild(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                                 neurodata_type_def='Foo',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data', attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(Foo, self.foo_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        builder1 = self.build_manager.build(container_inst)
        self.assertDictEqual(builder1, expected)

    def test_memoization(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        builder1 = self.build_manager.build(container_inst)
        builder2 = self.build_manager.build(container_inst)
        self.assertDictEqual(builder1, expected)
        self.assertIs(builder1, builder2)


class TestBuildManagerConstruct(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                                 neurodata_type_def='Foo',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                      attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(Foo, self.foo_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        builder = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        expected = Foo('my_foo', list(range(10)), 'value1', 10)
        container = self.build_manager.construct(builder)
        self.assertListEqual(container.data, list(range(10)))
        self.assertEqual(container.attr1, 'value1')
        self.assertEqual(container.attr2, 10)

    def test_memoization(self):
        builder = GroupBuilder('my_foo', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        expected = Foo('my_foo', list(range(10)), 'value1', 10)
        container1 = self.build_manager.construct(builder)
        container2 = self.build_manager.construct(builder)
        self.assertIs(container1, container2)


class TestContainingContainer(unittest.TestCase):
    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                                 neurodata_type_def='Foo',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                                      attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])
        self.type_map.register_spec(Foo, self.foo_spec)
        self.build_manager = BuildManager(self.type_map)

    def test_default_mapping(self):
        ''' Test default mapping for an NWBContainer that has an NWBContainer as an attribute value '''
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                                    name="my foo bucket",
                                    neurodata_type_def='FooBucket',
                                    groups=[GroupSpec('the Foos in this bucket', neurodata_type='Foo')])
        self.type_map.register_spec(FooBucket, self.bucket_spec)
        foo1 = Foo('my_foo1', list(range(10)), 'value1', 10)
        foo2 = Foo('my_foo2', list(range(10, 20)), 'value2', 20)
        foos = [foo1, foo2]
        bucket = FooBucket('test_foo_bucket', foos)
        foo_builder1 = GroupBuilder('my_foo1', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        foo_builder2 = GroupBuilder('my_foo2', datasets={'data': DatasetBuilder('data', list(range(10, 20)), attributes={'attr2': 20})},
                                attributes={'attr1': 'value2', 'neurodata_type': 'Foo'})
        foo_builders = {'my_foo1': foo_builder1,'my_foo2':  foo_builder2}
        expected = GroupBuilder('test_foo_bucket', groups=foo_builders, attributes={'neurodata_type': 'FooBucket'})
        builder = self.build_manager.build(bucket)
        self.assertDictEqual(builder, expected)

    def test_default_mapping_additional_group(self):
        ''' Test default mapping for an NWBContainer that has an NWBContainer as an attribute value
            when those containers go into their own subgroup
        '''
        tmp_spec = GroupSpec('A subgroup for Foos', 'foos', groups=[GroupSpec('the Foos in this bucket', neurodata_type='Foo')])
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                                    name="my foo bucket",
                                    neurodata_type_def='FooBucket',
                                    groups=[tmp_spec])
        self.type_map.register_spec(FooBucket, self.bucket_spec)
        foo1 = Foo('my_foo1', list(range(10)), 'value1', 10)
        foo2 = Foo('my_foo2', list(range(10, 20)), 'value2', 20)
        foos = [foo1, foo2]
        foos = [foo1]
        bucket = FooBucket('test_foo_bucket', foos)
        foo_builder1 = GroupBuilder('my_foo1', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        foo_builder2 = GroupBuilder('my_foo2', datasets={'data': DatasetBuilder('data', list(range(10, 20)), attributes={'attr2': 20})},
                                attributes={'attr1': 'value2', 'neurodata_type': 'Foo'})
        foo_builders = {'my_foo1': foo_builder1,'my_foo2':  foo_builder2}
        foo_builders = {'my_foo1': foo_builder1}
        expected = GroupBuilder('test_foo_bucket', groups={'foo': GroupBuilder('foos', groups=foo_builders)}, attributes={'neurodata_type': 'FooBucket'})
        builder = self.build_manager.build(bucket)
        self.assertDictEqual(builder, expected)

    def test_default_mapping_additional_group_nested(self):
        ''' Test default mapping for an NWBContainer that has an NWBContainer as an attribute value
            when those containers go into their own subgroup of another subgroup
        '''
        tmp_spec = GroupSpec('A subgroup for Foos', 'foos', groups=[GroupSpec('the Foos in this bucket', neurodata_type='Foo')])
        tmp_spec = GroupSpec('A subgroup to hold the subgroup', 'foo_holder', groups=[tmp_spec])
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                                    name="my foo bucket",
                                    neurodata_type_def='FooBucket',
                                    groups=[tmp_spec])
        self.type_map.register_spec(FooBucket, self.bucket_spec)
        foo1 = Foo('my_foo1', list(range(10)), 'value1', 10)
        foo2 = Foo('my_foo2', list(range(10, 20)), 'value2', 20)
        foos = [foo1, foo2]
        bucket = FooBucket('test_foo_bucket', foos)
        foo_builder1 = GroupBuilder('my_foo1', datasets={'data': DatasetBuilder('data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'neurodata_type': 'Foo'})
        foo_builder2 = GroupBuilder('my_foo2', datasets={'data': DatasetBuilder('data', list(range(10, 20)), attributes={'attr2': 20})},
                                attributes={'attr1': 'value2', 'neurodata_type': 'Foo'})
        foo_builders = {'my_foo1': foo_builder1,'my_foo2':  foo_builder2}
        expected = GroupBuilder('test_foo_bucket', groups={'foo_holder':
                                                                GroupBuilder('foo_holder', groups={'foo':
                                                                    GroupBuilder('foos', groups=foo_builders)})}, attributes={'neurodata_type': 'FooBucket'})
        builder = self.build_manager.build(bucket)
        self.assertDictEqual(builder, expected)

#TODO:
class TestWildCardNamedSpecs(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
