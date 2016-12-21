import unittest

from pynwb.io.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec

import json

class AttributeSpecTests(unittest.TestCase):

    def test_constructor(self):
        spec = AttributeSpec('attribute1',
                             'str',
                             'my first attribute')
        self.assertEqual(spec['name'], 'attribute1')
        self.assertEqual(spec['type'], 'str')
        self.assertEqual(spec['doc'], 'my first attribute')
        self.assertIsNone(spec.parent)
        json.dumps(spec)
        

class DatasetSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
        ]

    def test_constructor(self):
        spec = DatasetSpec('int', 
                           'dataset1',
                           doc='my first dataset',
                           attributes=self.attributes)
        self.assertEqual(spec['type'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertTrue(spec['linkable'])
        self.assertNotIn('nwb_type', spec)
        self.assertListEqual(spec['attributes'], self.attributes)
        json.dumps(spec)
                             
    def test_constructor_nwbtype(self):
        spec = DatasetSpec('int', 
                           'dataset1',
                           dimension=(None, None),
                           doc='my first dataset',
                           attributes=self.attributes,
                           linkable=False,
                           nwb_type='EphysData')
        self.assertEqual(spec['type'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertEqual(spec['nwb_type'], 'EphysData')
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        json.dumps(spec)

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
            DatasetSpec('int', 
                        'dataset1',
                        doc='my first dataset',
                        attributes=dset1_attributes,
                        linkable=True),
            DatasetSpec('int', 
                        'dataset2',
                        dimension=(None, None),
                        doc='my second dataset',
                        attributes=dset2_attributes,
                        linkable=True,
                        nwb_type='EphysData')
        ] 

        self.subgroups = [
            GroupSpec('subgroup1',
                      linkable=False),
            GroupSpec('subgroup2',
                      linkable=False)

        ]

    def test_constructor(self):
        spec = GroupSpec('root',
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False)
        
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertNotIn('nwb_type', spec)
        json.dumps(spec)
                             
    def test_constructor_nwbtype(self):
        spec = GroupSpec('root',
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False,
                         nwb_type='EphysData')
        
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertEqual(spec['nwb_type'], 'EphysData')
        json.dumps(spec)

    def test_set_dataset(self):
        spec = GroupSpec('root_test_set_dataset',
                         linkable=False,
                         nwb_type='EphysData')
        print("root test_set_dataset spec (%d): %s" % (id(spec), json.dumps(spec, indent=2)))
        spec.set_dataset(self.datasets[0])
        spec.set_dataset(self.datasets[1])
        self.assertListEqual(spec['datasets'], self.datasets)
        json.dumps(spec)

    def test_set_group(self):
        spec_ABCD = GroupSpec('root_test_set_group',
                         linkable=False,
                         nwb_type='EphysData')
        print("root test_set_group spec (%d): %s" % (id(spec_ABCD), json.dumps(spec_ABCD, indent=2)))
        #print("subgroup1 spec: %s" % json.dumps(self.subgroups[0], indent=2))
        #print("subgroup2 spec: %s" % json.dumps(self.subgroups[1], indent=2))
        #spec_ABCD.set_group(self.subgroups[0])
        #spec_ABCD.set_group(self.subgroups[1])
        #self.assertListEqual(spec_ABCD['groups'], self.subgroups)
        json.dumps(spec_ABCD)
