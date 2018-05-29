import unittest2 as unittest
import json

from pynwb.form.spec import GroupSpec, DatasetSpec, AttributeSpec, DtypeSpec, DtypeHelper, RefSpec

class DtypeSpecHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_recommended_dtypes(self):
        self.assertListEqual(DtypeHelper.recommended_primary_dtypes,
                             list(DtypeHelper.primary_dtype_synonyms.keys()))

    def test_valid_primary_dtypes(self):
        a = set(list(DtypeHelper.primary_dtype_synonyms.keys()) + [vi for v in DtypeHelper.primary_dtype_synonyms.values()
                                                               for vi in v] + ['number', ])
        self.assertSetEqual(a, DtypeHelper.valid_primary_dtypes)

    def test_simplify_cpd_type(self):
        compound_type =  [DtypeSpec('test', 'test field', 'float'),
                          DtypeSpec('test2', 'test field2', 'int')]
        expected_result = ['float', 'int']
        result = DtypeHelper.simplify_cpd_type(compound_type)
        self.assertListEqual(result, expected_result)


class DtypeSpecTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_constructor(self):
        spec = DtypeSpec('column1', 'an example column', 'int')
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

    def test_build_spec(self):
        spec = DtypeSpec.build_spec({'doc': 'an example column', 'name': 'column1', 'dtype': 'int'})
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')


class DatasetSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'my first attribute', 'text'),
            AttributeSpec('attribute2', 'my second attribute', 'text')
        ]

    def test_constructor(self):
        spec = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           attributes=self.attributes)
        self.assertEqual(spec['dtype'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertNotIn('linkable', spec)
        self.assertNotIn('data_type_def', spec)
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        json.dumps(spec)

    def test_constructor_nwbtype(self):
        spec = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           namespace='core',
                           data_type_def='EphysData')
        self.assertEqual(spec['dtype'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertEqual(spec['data_type_def'], 'EphysData')
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)

    def test_constructor_invalidate_dtype(self):
        with self.assertRaises(ValueError):
            DatasetSpec(doc='my first dataset',
                        dtype='my bad dtype',     # <-- Expect AssertionError due to bad type
                        name='dataset1',
                        dimension=(None, None),
                        attributes=self.attributes,
                        linkable=False,
                        namespace='core',
                        data_type_def='EphysData')

    def test_constructor_ref_spec(self):
        dtype = RefSpec('TimeSeries', 'object')
        spec = DatasetSpec(doc='my first dataset',
                           dtype=dtype,
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           namespace='core',
                           data_type_def='EphysData')
        self.assertDictEqual(spec['dtype'], dtype)

    def test_datatype_extension(self):
        base = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           namespace='core',
                           data_type_def='EphysData')

        attributes = [AttributeSpec('attribute3', 'my first extending attribute', 'float')]
        ext = DatasetSpec('my first dataset extension',
                          'int',
                          name='dataset1',
                          dimension=(None, None),
                          attributes=attributes,
                          linkable=False,
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='SpikeData')
        self.assertDictEqual(ext['attributes'][0], attributes[0])
        self.assertDictEqual(ext['attributes'][1], self.attributes[0])
        self.assertDictEqual(ext['attributes'][2], self.attributes[1])
        ext_attrs = ext.attributes
        self.assertIs(ext, ext_attrs[0].parent)
        self.assertIs(ext, ext_attrs[1].parent)
        self.assertIs(ext, ext_attrs[2].parent)

    def test_datatype_extension_groupspec(self):
        '''Test to make sure DatasetSpec catches when a GroupSpec used as data_type_inc'''
        base = GroupSpec('a fake grop',
                         namespace='core',
                         data_type_def='EphysData')
        with self.assertRaises(TypeError):
            ext = DatasetSpec('my first dataset extension',  # noqa: F841
                              'int',
                              name='dataset1',
                              namespace='core',
                              data_type_inc=base,
                              data_type_def='SpikeData')

    def test_constructor_table(self):
        dtype1 = DtypeSpec('column1', 'the first column', 'int')
        dtype2 = DtypeSpec('column2', 'the second column', 'float')
        spec = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           name='table1',
                           attributes=self.attributes)
        self.assertEqual(spec['dtype'], [dtype1, dtype2])
        self.assertEqual(spec['name'], 'table1')
        self.assertEqual(spec['doc'], 'my first table')
        self.assertNotIn('linkable', spec)
        self.assertNotIn('data_type_def', spec)
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        json.dumps(spec)

    def test_datatype_table_extension(self):
        dtype1 = DtypeSpec('column1', 'the first column', 'int')
        dtype2 = DtypeSpec('column2', 'the second column', 'float')
        base = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           attributes=self.attributes,
                           namespace='core',
                           data_type_def='SimpleTable')
        self.assertEqual(base['dtype'], [dtype1, dtype2])
        self.assertEqual(base['doc'], 'my first table')
        dtype3 = DtypeSpec('column3', 'the third column', 'text')
        ext = DatasetSpec('my first table extension',
                          [dtype3],
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='ExtendedTable')
        self.assertEqual(ext['dtype'], [dtype1, dtype2, dtype3])
        self.assertEqual(ext['doc'], 'my first table extension')

    def test_datatype_table_extension_higher_precision(self):
        dtype1 = DtypeSpec('column1', 'the first column', 'int')
        dtype2 = DtypeSpec('column2', 'the second column', 'float32')
        base = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           attributes=self.attributes,
                           namespace='core',
                           data_type_def='SimpleTable')
        self.assertEqual(base['dtype'], [dtype1, dtype2])
        self.assertEqual(base['doc'], 'my first table')
        dtype3 = DtypeSpec('column2', 'the second column, with greater precision', 'float64')
        ext = DatasetSpec('my first table extension',
                          [dtype3],
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='ExtendedTable')
        self.assertEqual(ext['dtype'], [dtype1, dtype3])
        self.assertEqual(ext['doc'], 'my first table extension')

    def test_datatype_table_extension_lower_precision(self):
        dtype1 = DtypeSpec('column1', 'the first column', 'int')
        dtype2 = DtypeSpec('column2', 'the second column', 'float64')
        base = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           attributes=self.attributes,
                           namespace='core',
                           data_type_def='SimpleTable')
        self.assertEqual(base['dtype'], [dtype1, dtype2])
        self.assertEqual(base['doc'], 'my first table')
        dtype3 = DtypeSpec('column2', 'the second column, with greater precision', 'float32')
        with self.assertRaisesRegex(ValueError, 'Cannot extend float64 to float32'):
            ext = DatasetSpec('my first table extension',  # noqa: F841
                              [dtype3],
                              namespace='core',
                              data_type_inc=base,
                              data_type_def='ExtendedTable')

    def test_datatype_table_extension_diff_format(self):
        dtype1 = DtypeSpec('column1', 'the first column', 'int')
        dtype2 = DtypeSpec('column2', 'the second column', 'float64')
        base = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           attributes=self.attributes,
                           namespace='core',
                           data_type_def='SimpleTable')
        self.assertEqual(base['dtype'], [dtype1, dtype2])
        self.assertEqual(base['doc'], 'my first table')
        dtype3 = DtypeSpec('column2', 'the second column, with greater precision', 'int32')
        with self.assertRaisesRegex(ValueError, 'Cannot extend float64 to int32'):
            ext = DatasetSpec('my first table extension',  # noqa: F841
                          [dtype3],
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='ExtendedTable')
