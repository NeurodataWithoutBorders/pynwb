import unittest
import json

from form.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec, SpecCatalog


class DatasetSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
        ]
        self.ndt_attr_spec = AttributeSpec('data_type', 'text', 'the data type of this object', value='EphysData')
        self.ns_attr_spec = AttributeSpec('namespace', 'text', 'the namespace for the data type of this object', required=False)

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

    def test_nwbtype_extension(self):
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
        ndt_attr_spec = AttributeSpec('data_type', 'text', 'the data type of this object', value='SpikeData')
        self.assertDictEqual(ext['attributes'][0], attributes[0])
        self.assertDictEqual(ext['attributes'][1], self.attributes[0])
        self.assertDictEqual(ext['attributes'][2], self.attributes[1])
        ext_attrs = ext.attributes
        self.assertIs(ext, ext_attrs[0].parent)
        self.assertIs(ext, ext_attrs[1].parent)
        self.assertIs(ext, ext_attrs[2].parent)
        self.assertIs(ext, ext_attrs[3].parent)
        self.assertIs(ext, ext_attrs[4].parent)
