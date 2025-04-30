'''
Tests for NWB specific Spec classes

This should really test to make sure neurodata_type_def and neurodata_type_inc
gets mapped appropriately when constructors and methods are invoked
'''
import json

from pynwb.spec import (
    NWBNamespaceBuilder, 
    NWBRefSpec, 
    NWBLinkSpec, 
    NWBDtypeSpec,
    NWBGroupSpec, 
    NWBDatasetSpec
)
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


class NWBLinkSpecTest(TestCase):

    def test_constructor(self):
        spec = NWBLinkSpec(
            doc='A test link',
            target_type='TimeSeries',
            quantity='+',
            name='Link1',
        )
        self.assertEqual(spec.doc, 'A test link')
        self.assertEqual(spec.target_type, 'TimeSeries')
        self.assertEqual(spec.data_type_inc, 'TimeSeries')
        self.assertEqual(spec.quantity, '+')
        self.assertEqual(spec.name, 'Link1')
        json.dumps(spec)


class NWBDtypeSpecTest(TestCase):

    def test_constructor(self):
        spec = NWBDtypeSpec('column1', 'an example column', 'int')
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

class NWBGroupSpecTest(TestCase):

    def test_constructor(self):
        spec = NWBGroupSpec(
            doc='A test group',
            neurodata_type_def='TimeSeries',
            neurodata_type_inc='NWBData',
            linkable=True,
            name='Group1',
        )
        self.assertEqual(spec.doc, 'A test group')
        self.assertEqual(spec.neurodata_type_def, 'TimeSeries')
        self.assertEqual(spec.neurodata_type_inc, 'NWBData')
        self.assertEqual(spec.linkable, True)
        self.assertEqual(spec.name, 'Group1')
        json.dumps(spec)

    def test_add_group(self):
        spec = NWBGroupSpec(
            doc='A test group',
            neurodata_type_def='TimeSeries',
            neurodata_type_inc='NWBData',
            linkable=True,
            name='Group1',
        )
        spec.add_group(
            doc='A test group',
            neurodata_type_def='TimeSeries',
            neurodata_type_inc='NWBData',
            linkable=True,
            name='Group2',
        )
        self.assertEqual(len(spec.groups), 1)
        self.assertEqual(spec.groups[0].name, 'Group2')
        self.assertIsInstance(spec.groups[0], NWBGroupSpec)

    def test_add_dataset(self):
        spec = NWBGroupSpec(
            doc='A test group',
            neurodata_type_def='TimeSeries',
            neurodata_type_inc='NWBData',
            linkable=True,
            name='Group1',
        )
        spec.add_dataset(
            doc='A test dataset',
            name='dataset1',
            dtype='int',
            shape=(None,),
            dims=('time',),
            quantity='?',
        )
        self.assertEqual(len(spec.datasets), 1)
        self.assertEqual(spec.datasets[0].name, 'dataset1')
        self.assertIsInstance(spec.datasets[0], NWBDatasetSpec)
