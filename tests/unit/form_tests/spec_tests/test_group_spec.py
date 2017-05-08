import unittest
import json

from form.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec, SpecCatalog

class GroupSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
       ]

        dset1_attributes = [
            AttributeSpec('attribute3', 'str', 'my third attribute'),
            AttributeSpec('attribute4', 'str', 'my fourth attribute')
        ]

        dset2_attributes = [
            AttributeSpec('attribute5', 'str', 'my fifth attribute'),
            AttributeSpec('attribute6', 'str', 'my sixth attribute')
        ]

        self.datasets = [
            DatasetSpec('my first dataset',
                        'int',
                        name='dataset1',
                        attributes=dset1_attributes,
                        linkable=True),
            DatasetSpec('my second dataset',
                        'int',
                        name='dataset2',
                        dimension=(None, None),
                        attributes=dset2_attributes,
                        linkable=True,
                        namespace='core',
                        data_type_def='EphysData')
        ]

        self.subgroups = [
            GroupSpec('A test subgroup',
                      name='subgroup1',
                      linkable=False),
            GroupSpec('A test subgroup',
                      name='subgroup2',
                      linkable=False)

        ]
        self.ndt_attr_spec = AttributeSpec('data_type', 'text', 'the data type of this object', value='EphysData')
        self.ns_attr_spec = AttributeSpec('namespace', 'text', 'the namespace for the data type of this object', value='core')

    def test_constructor(self):
        spec = GroupSpec('A test group',
                          name='root_constructor',
                         groups=self.subgroups,
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False)
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertNotIn('data_type_def', spec)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        json.dumps(spec)

    def test_constructor_nwbtype(self):
        spec = GroupSpec('A test group',
                         name='root_constructor_nwbtype',
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False,
                         namespace='core',
                         data_type_def='EphysData')
        self.assertFalse(spec['linkable'])
        self.assertDictEqual(spec['attributes'][0], self.ndt_attr_spec)
        self.assertDictEqual(spec['attributes'][1], self.ns_attr_spec)
        self.assertListEqual(spec['attributes'][2:], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertEqual(spec['data_type_def'], 'EphysData')
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        json.dumps(spec)

    def test_set_dataset(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_dataset',
                         linkable=False,
                         namespace='core',
                         data_type_def='EphysData')
        spec.set_dataset(self.datasets[0])
        self.assertIs(spec, self.datasets[0].parent)

    def test_set_group(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_group',
                         linkable=False,
                         namespace='core',
                         data_type_def='EphysData')
        spec.set_group(self.subgroups[0])
        spec.set_group(self.subgroups[1])
        self.assertListEqual(spec['groups'], self.subgroups)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        json.dumps(spec)
