'''
Tests for NWB specific Spec classes

This should really test to make sure neurodata_type_def and neurodata_type_inc
gets mapped appropriately when constructors and methods are invoked
'''
import json

from pynwb.spec import NWBNamespaceBuilder, NWBRefSpec
from pynwb.testing import TestCase


class NWBNamespaceTest(TestCase):

    def test_constructor(self):
        self.ns_builder = NWBNamespaceBuilder("Frank Laboratory NWB Extensions", "franklab", version='0.1')


class NWBRefSpecTests(TestCase):

    def test_constructor(self):
        spec = NWBRefSpec('TimeSeries', 'object')
        self.assertEqual(spec.target_type, 'TimeSeries')
        self.assertEqual(spec.reftype, 'object')
        json.dumps(spec)  # to ensure there are no circular links

    def test_wrong_reference_type(self):
        with self.assertRaises(ValueError):
            NWBRefSpec('TimeSeries', 'unknownreftype')
