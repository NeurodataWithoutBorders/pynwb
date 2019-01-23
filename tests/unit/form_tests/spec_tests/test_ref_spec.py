import unittest2 as unittest
import json

from pynwb.form.spec import RefSpec


class RefSpecTests(unittest.TestCase):

    def test_constructor(self):
        spec = RefSpec('TimeSeries', 'object')
        self.assertEqual(spec.target_type, 'TimeSeries')
        self.assertEqual(spec.reftype, 'object')
        json.dumps(spec)  # to ensure there are no circular links

    def test_wrong_reference_type(self):
        with self.assertRaises(ValueError):
            RefSpec('TimeSeries', 'unknownreftype')

    def test_isregion(self):
        spec = RefSpec('TimeSeries', 'object')
        self.assertFalse(spec.is_region())
        spec = RefSpec('NWBData', 'region')
        self.assertTrue(spec.is_region())
