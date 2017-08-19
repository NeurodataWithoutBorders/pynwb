import unittest
import json

from form.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec, SpecCatalog, DtypeSpec

class DtypeSpecTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_constructor(self):
        spec = DtypeSpec('an example column', 'column1', 'int')
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

    def test_build_spec(self):
        spec = DtypeSpec.build_spec({'doc':'an example column', 'name': 'column1', 'dtype': 'int'})
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

class DatasetSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
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

    def test_datatype_extension(self):
        base = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           namespace='core',
                           data_type_def='EphysData')

        attributes = [AttributeSpec('attribute3', 'float', 'my first extending attribute')]
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
            ext = DatasetSpec('my first dataset extension',
                          'int',
                          name='dataset1',
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='SpikeData')

    def test_constructor_table(self):
        dtype1 = DtypeSpec('the first column', 'column1', 'int')
        dtype2 = DtypeSpec('the second column', 'column2', 'float')
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


    def test_datatype_extension(self):
        dtype1 = DtypeSpec('the first column', 'column1', 'int')
        dtype2 = DtypeSpec('the second column', 'column2', 'float')
        base = DatasetSpec('my first table',
                           [dtype1, dtype2],
                           attributes=self.attributes,
                           namespace='core',
                           data_type_def='SimpleTable')
        self.assertEqual(base['dtype'], [dtype1, dtype2])
        self.assertEqual(base['doc'], 'my first table')

        dtype3 = DtypeSpec('the third column', 'column3', 'str')
        ext = DatasetSpec('my first table extension',
                          [dtype3],
                          namespace='core',
                          data_type_inc=base,
                          data_type_def='ExtendedTable')
        self.assertEqual(ext['dtype'], [dtype1, dtype2, dtype3])
        self.assertEqual(ext['doc'], 'my first table extension')



