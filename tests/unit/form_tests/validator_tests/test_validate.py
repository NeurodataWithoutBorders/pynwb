import unittest2 as unittest
from abc import ABCMeta, abstractmethod
from six import with_metaclass
from six import text_type as text

from pynwb.form.spec import GroupSpec, AttributeSpec, DatasetSpec, SpecCatalog, SpecNamespace
from pynwb.form.build import GroupBuilder, DatasetBuilder
from pynwb.form.validate import ValidatorMap
from pynwb.form.validate.errors import *  # noqa: F403

CORE_NAMESPACE = 'test_core'


class ValidatorTestBase(with_metaclass(ABCMeta, unittest.TestCase)):

    def setUp(self):
        spec_catalog = SpecCatalog()
        for spec in self.getSpecs():
            spec_catalog.register_spec(spec, 'test.yaml')
        self.namespace = SpecNamespace(
            'a test namespace', CORE_NAMESPACE, [{'source': 'test.yaml'}], catalog=spec_catalog)
        self.vmap = ValidatorMap(self.namespace)

    @abstractmethod
    def getSpecs(self):
        pass


class TestEmptySpec(ValidatorTestBase):

    def getSpecs(self):
        return (GroupSpec('A test group specification with a data type', data_type_def='Bar'),)

    def test_valid(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar'})
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 0)

    def test_invalid_missing_req_type(self):
        builder = GroupBuilder('my_bar')
        err_msg = "builder must have data type defined with attribute '[A-Za-z_]+'"
        with self.assertRaisesRegex(ValueError, err_msg):
            result = self.vmap.validate(builder)  # noqa: F841


class TestBasicSpec(ValidatorTestBase):

    def getSpecs(self):
        ret = GroupSpec('A test group specification with a data type',
                        data_type_def='Bar',
                        datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                              attributes=[AttributeSpec(
                                                  'attr2', 'an example integer attribute', 'int')])],
                        attributes=[AttributeSpec('attr1', 'an example string attribute', 'text')])
        return (ret,)

    def test_invalid_missing(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar'})
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], MissingError)  # noqa: F405
        self.assertEqual(result[0].name, 'Bar/attr1')
        self.assertIsInstance(result[1], MissingError)  # noqa: F405
        self.assertEqual(result[1].name, 'Bar/data')

    def test_invalid_incorrect_type_get_validator(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar', 'attr1': 10})
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], DtypeError)  # noqa: F405
        self.assertEqual(result[0].name, 'Bar/attr1')
        self.assertIsInstance(result[1], MissingError)  # noqa: F405
        self.assertEqual(result[1].name, 'Bar/data')

    def test_invalid_incorrect_type_validate(self):
        builder = GroupBuilder('my_bar', attributes={'data_type': 'Bar', 'attr1': 10})
        result = self.vmap.validate(builder)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], DtypeError)  # noqa: F405
        self.assertEqual(result[0].name, 'Bar/attr1')
        self.assertIsInstance(result[1], MissingError)  # noqa: F405
        self.assertEqual(result[1].name, 'Bar/data')

    def test_valid(self):
        builder = GroupBuilder('my_bar',
                               attributes={'data_type': 'Bar', 'attr1': text('a string attribute')},
                               datasets=[DatasetBuilder('data', 100, attributes={'attr2': 10})])
        validator = self.vmap.get_validator('Bar')
        result = validator.validate(builder)
        self.assertEqual(len(result), 0)


class TestNestedTypes(ValidatorTestBase):

    def getSpecs(self):
        bar = GroupSpec('A test group specification with a data type',
                        data_type_def='Bar',
                        datasets=[DatasetSpec('an example dataset', 'int', name='data',
                                              attributes=[AttributeSpec('attr2', 'an example integer attribute',
                                                                        'int')])],
                        attributes=[AttributeSpec('attr1', text('an example string attribute'), 'text')])
        foo = GroupSpec('A test group that contains a data type',
                        data_type_def='Foo',
                        groups=[GroupSpec('A Bar group for Foos', name='my_bar', data_type_inc='Bar')],
                        attributes=[AttributeSpec('foo_attr', 'a string attribute specified as text', 'text',
                                                  required=False)])

        return (bar, foo)

    def test_invalid_missing_req_type(self):
        foo_builder = GroupBuilder('my_foo', attributes={'data_type': 'Foo',
                                                         'foo_attr': text('example Foo object')})
        results = self.vmap.validate(foo_builder)
        self.assertIsInstance(results[0], MissingDataType)  # noqa: F405
        self.assertEqual(results[0].name, 'Foo')
        self.assertEqual(results[0].reason, 'missing data type Bar')

    def test_invalid_wrong_name_req_type(self):
        bar_builder = GroupBuilder('bad_bar_name',
                                   attributes={'data_type': 'Bar', 'attr1': 'a string attribute'},
                                   datasets=[DatasetBuilder('data', 100, attributes={'attr2': 10})])

        foo_builder = GroupBuilder('my_foo',
                                   attributes={'data_type': 'Foo', 'foo_attr': text('example Foo object')},
                                   groups=[bar_builder])

        results = self.vmap.validate(foo_builder)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], MissingDataType)  # noqa: F405
        self.assertEqual(results[0].data_type, 'Bar')

    def test_valid(self):
        bar_builder = GroupBuilder('my_bar',
                                   attributes={'data_type': 'Bar', 'attr1': text('a string attribute')},
                                   datasets=[DatasetBuilder('data', 100, attributes={'attr2': 10})])

        foo_builder = GroupBuilder('my_foo',
                                   attributes={'data_type': 'Foo', 'foo_attr': text('example Foo object')},
                                   groups=[bar_builder])

        results = self.vmap.validate(foo_builder)
        self.assertEqual(len(results), 0)

    def test_valid_wo_opt_attr(self):
        bar_builder = GroupBuilder('my_bar',
                                   attributes={'data_type': 'Bar', 'attr1': text('a string attribute')},
                                   datasets=[DatasetBuilder('data', 100, attributes={'attr2': 10})])
        foo_builder = GroupBuilder('my_foo',
                                   attributes={'data_type': 'Foo'},
                                   groups=[bar_builder])

        results = self.vmap.validate(foo_builder)
        self.assertEqual(len(results), 0)
