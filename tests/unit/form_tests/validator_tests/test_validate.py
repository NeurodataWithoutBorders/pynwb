import unittest

from form.spec import GroupSpec, AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace, NamespaceCatalog
from form.build import GroupBuilder, DatasetBuilder, ObjectMapper, BuildManager, TypeMap

from form.validate import ValidatorMap

CORE_NAMESPACE = 'test_core'

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.bar_spec = self.getBarSpec()
        spec_catalog = SpecCatalog()
        spec_catalog.register_spec(self.bar_spec, 'test.yaml')
        self.namespace = SpecNamespace('a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=spec_catalog)
        self.vmap = ValidatorMap(self.namespace)

    def getBarSpec(self):
        return GroupSpec('A test group specification with a data type', data_type_def='Bar')

    def test_validate(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar'})
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 0)

class TestSpec(BaseTest):

    def getBarSpec(self):
        return GroupSpec('A test group specification with a data type',
                         data_type_def='Bar',
                         datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                        attributes=[AttributeSpec('attr2', 'int', 'an example integer attribute')])],
                         attributes=[AttributeSpec('attr1', 'str', 'an example string attribute')])

    def test_validate(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar'})
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 2)
