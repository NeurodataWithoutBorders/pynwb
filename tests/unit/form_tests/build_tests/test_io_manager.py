import unittest
from abc import ABCMeta, abstractmethod

from pynwb.core import NWBContainer

from form.spec import GroupSpec, AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace, NamespaceCatalog
from form.spec.spec import ZERO_OR_MANY
from form.build import GroupBuilder, DatasetBuilder
from form.utils import docval, getargs
from form.build import ObjectMapper, BuildManager, TypeMap

CORE_NAMESPACE = 'core'

class Foo(NWBContainer):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this Foo'},
            {'name': 'my_data', 'type': list, 'doc': 'some data'},
            {'name': 'attr1', 'type': str, 'doc': 'an attribute'},
            {'name': 'attr2', 'type': int, 'doc': 'another attribute'},
            {'name': 'attr3', 'type': float, 'doc': 'a third attribute', 'default': 3.14})
    def __init__(self, **kwargs):
        name, my_data, attr1, attr2, attr3 = getargs('name', 'my_data', 'attr1', 'attr2', 'attr3', kwargs)
        super(Foo, self).__init__()
        self.__name = name
        self.__data = my_data
        self.__attr1 = attr1
        self.__attr2 = attr2
        self.__attr3 = attr3

    def __eq__(self, other):
        attrs = ('name', 'my_data', 'attr1', 'attr2', 'attr3')
        return all(getattr(self, a) == getattr(other, a) for a in attrs)

    def __str__(self):
        attrs = ('name', 'my_data', 'attr1', 'attr2', 'attr3')
        return '<' + ','.join('%s=%s' % (a, getattr(self, a)) for a in attrs) + '>'

    @property
    def name(self):
        return self.__name

    @property
    def my_data(self):
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

    def __hash__(self):
        return hash(self.name)

class FooBucket(NWBContainer):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this bucket'},
            {'name': 'foos', 'type': list, 'doc': 'the Foo objects in this bucket', 'default': list()})
    def __init__(self, **kwargs):
        name, foos = getargs('name', 'foos', kwargs)
        super(FooBucket, self).__init__()
        self.__name = name
        self.__foos = foos

    def __eq__(self, other):
        return self.name == other.name and set(self.foos) == set(other.foos)

    def __str__(self):
        foo_str = "[" + ",".join(str(f) for f in self.foos) + "]"
        return 'name=%s, foos=%s' % (self.name, foo_str)

    @property
    def name(self):
        return self.__name

    @property
    def foos(self):
        return self.__foos

class TestBase(unittest.TestCase):

    def setUp(self):
        self.foo_spec = GroupSpec('A test group specification with a neurodata type',
                                 namespace=CORE_NAMESPACE,
                                 neurodata_type_def='Foo',
                                 datasets=[DatasetSpec('an example dataset', 'int', name='my_data',
                                                       attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                                 attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])

        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.foo_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog(CORE_NAMESPACE)
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Foo', Foo)
        self.type_map.register_map(Foo, ObjectMapper)
        self.manager = BuildManager(self.type_map)



class TestBuildManager(TestBase):

    def test_build(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_foo', datasets={'my_data': DatasetBuilder('my_data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'})
        builder1 = self.manager.build(container_inst)
        self.assertDictEqual(builder1, expected)

    def test_build_memoization(self):
        container_inst = Foo('my_foo', list(range(10)), 'value1', 10)
        expected = GroupBuilder('my_foo', datasets={'my_data': DatasetBuilder('my_data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'})
        builder1 = self.manager.build(container_inst)
        builder2 = self.manager.build(container_inst)
        self.assertDictEqual(builder1, expected)
        self.assertIs(builder1, builder2)

    def test_construct(self):
        builder = GroupBuilder('my_foo', datasets={'my_data': DatasetBuilder('my_data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'})
        expected = Foo('my_foo', list(range(10)), 'value1', 10)
        container = self.manager.construct(builder)
        self.assertListEqual(container.my_data, list(range(10)))
        self.assertEqual(container.attr1, 'value1')
        self.assertEqual(container.attr2, 10)

    def test_construct_memoization(self):
        builder = GroupBuilder('my_foo', datasets={'my_data': DatasetBuilder('my_data', list(range(10)), attributes={'attr2': 10})},
                                attributes={'attr1': 'value1', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'})
        expected = Foo('my_foo', list(range(10)), 'value1', 10)
        container1 = self.manager.construct(builder)
        container2 = self.manager.construct(builder)
        self.assertIs(container1, container2)

class TestNestedBase(TestBase):

    def setUp(self):
        if type(self) == TestNestedBase:
            raise unittest.SkipTest('Abstract Base Class')
        super(TestNestedBase, self).setUp()
        self.foo_bucket = FooBucket('test_foo_bucket', [
                            Foo('my_foo1', list(range(10)), 'value1', 10),
                            Foo('my_foo2', list(range(10, 20)), 'value2', 20)])
        self.foo_builders = {
            'my_foo1': GroupBuilder('my_foo1', datasets={'my_data': DatasetBuilder('my_data', list(range(10)), attributes={'attr2': 10})},
                                                                                attributes={'attr1': 'value1', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'}),
            'my_foo2': GroupBuilder('my_foo2', datasets={'my_data': DatasetBuilder('my_data', list(range(10, 20)), attributes={'attr2': 20})},
                                                                                attributes={'attr1': 'value2', 'namespace': CORE_NAMESPACE, 'neurodata_type': 'Foo'})
        }
        self.setUpBucketBuilder()
        self.setUpBucketSpec()

        #self.spec_catalog = SpecCatalog()
        #self.spec_catalog.register_spec(self.bucket_spec, 'test.yaml')
        #self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=self.spec_catalog)
        #self.namespace_catalog = NamespaceCatalog(CORE_NAMESPACE)
        #self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        #self.type_map = TypeMap(self.namespace_catalog)

        self.spec_catalog.register_spec(self.bucket_spec, 'test.yaml')
        self.type_map.register_container_type(CORE_NAMESPACE, 'FooBucket', FooBucket)
        self.type_map.register_map(FooBucket, ObjectMapper)
        self.manager = BuildManager(self.type_map)

    def setUpBucketBuilder(self):
        pass

    def setUpBucketSpec(self):
        pass

    def test_build(self):
        ''' Test default mapping for an NWBContainer that has an NWBContainer as an attribute value '''
        builder = self.manager.build(self.foo_bucket)
        print("EXPECTED: ", self.bucket_builder)
        print("RECEIVED: ", builder)
        self.assertDictEqual(builder, self.bucket_builder)

    def test_construct(self):
        container = self.manager.construct(self.bucket_builder)
        self.assertEqual(container, self.foo_bucket)

class TestNestedContainersNoSubgroups(TestNestedBase):
    '''
        Test BuildManager.build and BuildManager.construct when the
        NWBContainer contains other NWBContainers, but does not keep them in
        additional subgroups
    '''

    def setUpBucketBuilder(self):
        self.bucket_builder = GroupBuilder('test_foo_bucket', groups=self.foo_builders, attributes={'namespace': CORE_NAMESPACE, 'neurodata_type': 'FooBucket'})

    def setUpBucketSpec(self):
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                                     name="test_foo_bucket",
                                     namespace=CORE_NAMESPACE,
                                     neurodata_type_def='FooBucket',
                                     groups=[GroupSpec('the Foos in this bucket', namespace=CORE_NAMESPACE, neurodata_type='Foo', quantity=ZERO_OR_MANY)])
        #self.type_map.register_spec(FooBucket, self.bucket_spec)

class TestNestedContainersSubgroup(TestNestedBase):

    def setUpBucketBuilder(self):
        tmp_builder = GroupBuilder('foos', groups=self.foo_builders)
        self.bucket_builder = GroupBuilder('test_foo_bucket', groups={'foos': tmp_builder}, attributes={'namespace': CORE_NAMESPACE, 'neurodata_type': 'FooBucket'})

    def setUpBucketSpec(self):
        tmp_spec = GroupSpec('A subgroup for Foos', 'foos', groups=[GroupSpec('the Foos in this bucket', namespace=CORE_NAMESPACE, neurodata_type='Foo', quantity=ZERO_OR_MANY)])
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                               name="test_foo_bucket",
                               namespace=CORE_NAMESPACE,
                               neurodata_type_def='FooBucket',
                               groups=[tmp_spec])
        #self.type_map.register_spec(FooBucket, self.bucket_spec)

class TestNestedContainersSubgroupSubgroup(TestNestedBase):

    def setUpBucketBuilder(self):
        tmp_builder = GroupBuilder('foos', groups=self.foo_builders)
        tmp_builder = GroupBuilder('foo_holder', groups={'foos': tmp_builder})
        self.bucket_builder = GroupBuilder('test_foo_bucket', groups={'foo_holder': tmp_builder}, attributes={'namespace': CORE_NAMESPACE, 'neurodata_type': 'FooBucket'})

    def setUpBucketSpec(self):
        tmp_spec = GroupSpec('A subgroup for Foos', 'foos', groups=[GroupSpec('the Foos in this bucket', namespace=CORE_NAMESPACE, neurodata_type='Foo', quantity=ZERO_OR_MANY)])
        tmp_spec = GroupSpec('A subgroup to hold the subgroup', 'foo_holder', groups=[tmp_spec])
        self.bucket_spec = GroupSpec('A test group specification for a neurodata type containing neurodata type',
                               name="test_foo_bucket",
                               namespace=CORE_NAMESPACE,
                               neurodata_type_def='FooBucket',
                               groups=[tmp_spec])
        #self.type_map.register_spec(FooBucket, bucket_spec)

#TODO:
class TestWildCardNamedSpecs(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
