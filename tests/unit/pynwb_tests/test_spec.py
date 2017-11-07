'''
Tests for NWB specific Spec classes

This should really test to make sure neurodata_type_def and neurodata_type_inc
gets mapped appropriately when constructors and methods are invoked
'''
import unittest

from pynwb.spec import NWBNamespaceBuilder

# create a builder for the namespace


class NWBNamespaceTest(unittest.TestCase):

    def test_constructor(self):
        self.ns_builder = NWBNamespaceBuilder("Frank Laboratory NWB Extensions", "franklab", version='0.1')
