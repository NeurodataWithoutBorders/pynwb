import unittest
import json

from form.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec, SpecCatalog


class AttributeSpecTests(unittest.TestCase):

    def test_constructor(self):
        spec = AttributeSpec('attribute1',
                             'str',
                             'my first attribute')
        self.assertEqual(spec['name'], 'attribute1')
        self.assertEqual(spec['dtype'], 'str')
        self.assertEqual(spec['doc'], 'my first attribute')
        self.assertIsNone(spec.parent)
        json.dumps(spec) # to ensure there are no circular links
