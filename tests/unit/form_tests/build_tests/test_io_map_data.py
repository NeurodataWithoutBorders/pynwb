import unittest2 as unittest

from pynwb.form.spec import AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace, NamespaceCatalog
from pynwb.form.build import DatasetBuilder, ObjectMapper, BuildManager, TypeMap
from pynwb.form import Data
from pynwb.form.utils import docval, getargs

CORE_NAMESPACE = 'test_core'


class Baz(Data):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this Baz'},
            {'name': 'data', 'type': list, 'doc': 'some data'},
            {'name': 'baz_attr', 'type': str, 'doc': 'an attribute'})
    def __init__(self, **kwargs):
        name, data, baz_attr = getargs('name', 'data', 'baz_attr', kwargs)
        super(Baz, self).__init__(name=name)
        self.__data = data
        self.__baz_attr = baz_attr

    @property
    def data(self):
        return self.__data

    @property
    def baz_attr(self):
        return self.__baz_attr


class TestDataMap(unittest.TestCase):

    def setUp(self):
        self.setUpBazSpec()
        self.spec_catalog = SpecCatalog()
        self.spec_catalog.register_spec(self.baz_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}],
                                       catalog=self.spec_catalog)
        self.namespace_catalog = NamespaceCatalog()
        self.namespace_catalog.add_namespace(CORE_NAMESPACE, self.namespace)
        self.type_map = TypeMap(self.namespace_catalog)
        self.type_map.register_container_type(CORE_NAMESPACE, 'Baz', Baz)
        self.type_map.register_map(Baz, ObjectMapper)
        self.manager = BuildManager(self.type_map)
        self.mapper = ObjectMapper(self.baz_spec)

    def setUpBazSpec(self):
        self.baz_spec = DatasetSpec('an Baz type', 'int', name='MyBaz', data_type_def='Baz',
                                    attributes=[AttributeSpec('baz_attr', 'an example string attribute', 'text')])

    def test_build(self):
        ''' Test default mapping functionality when no attributes are nested '''
        container = Baz('my_baz', list(range(10)), 'abcdefghijklmnopqrstuvwxyz')
        builder = self.mapper.build(container, self.manager)
        expected = DatasetBuilder('my_baz', list(range(10)), attributes={'baz_attr': 'abcdefghijklmnopqrstuvwxyz'})
        self.assertDictEqual(builder, expected)
