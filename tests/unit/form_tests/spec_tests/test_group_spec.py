import unittest2 as unittest
import json

from pynwb.form.spec import GroupSpec, DatasetSpec, AttributeSpec


class GroupSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'my first attribute', 'text'),
            AttributeSpec('attribute2', 'my second attribute', 'text')
        ]

        self.dset1_attributes = [
            AttributeSpec('attribute3', 'my third attribute', 'text'),
            AttributeSpec('attribute4', 'my fourth attribute', 'text')
        ]

        self.dset2_attributes = [
            AttributeSpec('attribute5', 'my fifth attribute', 'text'),
            AttributeSpec('attribute6', 'my sixth attribute', 'text')
        ]

        self.datasets = [
            DatasetSpec('my first dataset',
                        'int',
                        name='dataset1',
                        attributes=self.dset1_attributes,
                        linkable=True),
            DatasetSpec('my second dataset',
                        'int',
                        name='dataset2',
                        attributes=self.dset2_attributes,
                        linkable=True,
                        data_type_def='VoltageArray')
        ]

        self.subgroups = [
            GroupSpec('A test subgroup',
                      name='subgroup1',
                      linkable=False),
            GroupSpec('A test subgroup',
                      name='subgroup2',
                      linkable=False)

        ]
        self.ndt_attr_spec = AttributeSpec('data_type', 'the data type of this object', 'text', value='EphysData')
        self.ns_attr_spec = AttributeSpec('namespace', 'the namespace for the data type of this object',
                                          'text', required=False)

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
                         data_type_def='EphysData')
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertEqual(spec['data_type_def'], 'EphysData')
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        self.assertEqual(spec.data_type_def, 'EphysData')
        self.assertIsNone(spec.data_type_inc)
        json.dumps(spec)

    def test_set_dataset(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_dataset',
                         linkable=False,
                         data_type_def='EphysData')
        spec.set_dataset(self.datasets[0])
        self.assertIs(spec, self.datasets[0].parent)

    def test_set_group(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_group',
                         linkable=False,
                         data_type_def='EphysData')
        spec.set_group(self.subgroups[0])
        spec.set_group(self.subgroups[1])
        self.assertListEqual(spec['groups'], self.subgroups)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        json.dumps(spec)

    def test_type_extension(self):
        spec = GroupSpec('A test group',
                         name='parent_type',
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False,
                         data_type_def='EphysData')
        dset1_attributes_ext = [
            AttributeSpec('dset1_extra_attribute', 'an extra attribute for the first dataset', 'text')
        ]
        ext_datasets = [
            DatasetSpec('my first dataset extension',
                        'int',
                        name='dataset1',
                        attributes=dset1_attributes_ext,
                        linkable=True),
        ]
        ext_attributes = [
            AttributeSpec('ext_extra_attribute', 'an extra attribute for the group', 'text'),
        ]
        ext = GroupSpec('A test group extension',
                        name='child_type',
                        datasets=ext_datasets,
                        attributes=ext_attributes,
                        linkable=False,
                        data_type_inc=spec,
                        data_type_def='SpikeData')
        ext_dset1 = ext.get_dataset('dataset1')
        ext_dset1_attrs = ext_dset1.attributes
        self.assertDictEqual(ext_dset1_attrs[0], dset1_attributes_ext[0])
        self.assertDictEqual(ext_dset1_attrs[1], self.dset1_attributes[0])
        self.assertDictEqual(ext_dset1_attrs[2], self.dset1_attributes[1])
        self.assertEqual(ext.data_type_def, 'SpikeData')
        self.assertEqual(ext.data_type_inc, 'EphysData')

        ext_dset2 = ext.get_dataset('dataset2')
        self.maxDiff = None
        # this will suffice for now,  assertDictEqual doesn't do deep equality checks
        self.assertEqual(str(ext_dset2), str(self.datasets[1]))
        self.assertAttributesEqual(ext_dset2, self.datasets[1])

        # self.ns_attr_spec
        ndt_attr_spec = AttributeSpec('data_type', 'the data type of this object',  # noqa: F841
                                      'text', value='SpikeData')

        res_attrs = ext.attributes
        self.assertDictEqual(res_attrs[0], ext_attributes[0])
        self.assertDictEqual(res_attrs[1], self.attributes[0])
        self.assertDictEqual(res_attrs[2], self.attributes[1])

        # test that inherited specs are tracked appropriate
        for d in self.datasets:
            with self.subTest(dataset=d.name):
                self.assertTrue(ext.is_inherited_spec(d))
                self.assertFalse(spec.is_inherited_spec(d))

        json.dumps(spec)

    def assertDatasetsEqual(self, spec1, spec2):
        spec1_dsets = spec1.datasets
        spec2_dsets = spec2.datasets
        if len(spec1_dsets) != len(spec2_dsets):
            raise AssertionError('different number of AttributeSpecs')
        else:
            for i in range(len(spec1_dsets)):
                self.assertAttributesEqual(spec1_dsets[i], spec2_dsets[i])

    def assertAttributesEqual(self, spec1, spec2):
        spec1_attr = spec1.attributes
        spec2_attr = spec2.attributes
        if len(spec1_attr) != len(spec2_attr):
            raise AssertionError('different number of AttributeSpecs')
        else:
            for i in range(len(spec1_attr)):
                self.assertDictEqual(spec1_attr[i], spec2_attr[i])

    def test_add_attribute(self):
        spec = GroupSpec('A test group',
                         name='root_constructor',
                         groups=self.subgroups,
                         datasets=self.datasets,
                         linkable=False)
        for attrspec in self.attributes:
            spec.add_attribute(**attrspec)
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertNotIn('data_type_def', spec)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        self.assertIs(spec, spec.attributes[0].parent)
        self.assertIs(spec, spec.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        json.dumps(spec)

    def test_update_attribute_spec(self):
        spec = GroupSpec('A test group',
                         name='root_constructor',
                         attributes=[AttributeSpec('attribute1', 'my first attribute', 'text'), ])
        spec.set_attribute(AttributeSpec('attribute1', 'my first attribute', 'int', value=5))
        res = spec.get_attribute('attribute1')
        self.assertEqual(res.value, 5)
        self.assertEqual(res.dtype, 'int')
