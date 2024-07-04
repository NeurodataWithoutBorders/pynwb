'''
Tests for NWB specific Spec classes

This should really test to make sure neurodata_type_def and neurodata_type_inc
gets mapped appropriately when constructors and methods are invoked
'''
import json

from pynwb.spec import NWBNamespaceBuilder, NWBRefSpec, NWBDatasetSpec
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


class NWBDatasetSpecTests(TestCase):

    def test_special_value_skip(self):
        """Test whether value is removed from constructor kwargs for an exception DatasetSpec."""
        remove_value_names = ["bias_current", "bridge_balance", "capacitance_compensation"]
        for name in remove_value_names:
            dataset_spec_dict = dict(name=name, dtype="float", value=0.0, doc="doc")
            ret = NWBDatasetSpec.build_const_args(dataset_spec_dict)
            assert ret == dict(name=name, dtype="float", doc="doc")

            dataset_spec_dict = dict(name=name, dtype="float", value=0.0, doc="doc")
            obj = NWBDatasetSpec.build_spec(dataset_spec_dict)
            assert obj.name == name
            assert obj.dtype == "float"
            assert obj.doc == "doc"
            assert not hasattr(obj, "value")

    def test_extra_value_warn(self):
        """Test whether warning appears when adding "value" to a non-exception DatasetSpec."""
        dataset_spec_dict = dict(name="warnme", dtype="float", value=0.0, doc="doc")
        ret = NWBDatasetSpec.build_const_args(dataset_spec_dict)
        assert ret == dataset_spec_dict

        msg = "Unexpected keys ['value'] in spec {'name': 'warnme', 'dtype': 'float', 'value': 0.0, 'doc': 'doc'}"
        with self.assertWarnsWith(UserWarning, msg):
            obj = NWBDatasetSpec.build_spec(dataset_spec_dict)
            assert obj.name == "warnme"
            assert obj.dtype == "float"
            assert obj.doc == "doc"
            assert not hasattr(obj, "value")
