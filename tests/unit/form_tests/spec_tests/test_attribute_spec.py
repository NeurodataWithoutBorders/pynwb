import unittest2 as unittest
import json

from pynwb.form.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec, SpecCatalog


class AttributeSpecTests(unittest.TestCase):

    def test_constructor(self):
        spec = AttributeSpec('attribute1',
                             'my first attribute',
                             'str')
        self.assertEqual(spec['name'], 'attribute1')
        self.assertEqual(spec['dtype'], 'str')
        self.assertEqual(spec['doc'], 'my first attribute')
        self.assertIsNone(spec.parent)
        json.dumps(spec) # to ensure there are no circular links
