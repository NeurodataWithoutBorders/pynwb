# -*- coding: utf-8 -*-

#from .context import pynwb
from context import pynwb
import unittest

from pynwb.h5tools import GroupBuilder, DatasetBuilder, LinkBuilder, ExternalLinkBuilder, __iter_fill__, SOFT_LINK, HARD_LINK, EXTERNAL_LINK

import h5py
import os
import tempfile
import numpy as np
import json

class H5IOTest(unittest.TestCase):
    """Tests for h5tools IO tools"""


    def setUp(self):
        self.test_file_path = os.path.join(tempfile.gettempdir(), 'test.h5')
        self.f = h5py.File(self.test_file_path, 'w')

    def tearDown(self):
        self.f.close()
        os.remove(self.test_file_path)
        
    def test_iter_fill_divisible_chunks_data_fit(self):
        my_dset = __iter_fill__(self.f, 'test_dataset', range(100), 25)
        self.assertEqual(my_dset[99], 99)

    def test_iter_fill_divisible_chunks_data_nofit(self):
        my_dset = __iter_fill__(self.f, 'test_dataset', range(200), 25)
        self.assertEqual(my_dset[199], 199)

    def test_iter_fill_nondivisible_chunks_data_fit(self):
        my_dset = __iter_fill__(self.f, 'test_dataset', range(100), 30)
        self.assertEqual(my_dset[99], 99)

    def test_iter_fill_nondivisible_chunks_data_nofit(self):
        my_dset = __iter_fill__(self.f, 'test_dataset', range(200), 30)
        self.assertEqual(my_dset[199], 199)

class GroupBuilderSetterTests(unittest.TestCase):
    """Tests for setter functions in GroupBuilder class"""

    def setUp(self):
        setattr(self, 'gb', GroupBuilder())

    def tearDown(self):
        pass

    def test_setitem_disabled(self):
        """Test __set_item__ is disabled"""
        with self.assertRaises(NotImplementedError):
            self.gb['key'] = 'value'

    def test_add_dataset(self):
        ds = self.gb.add_dataset('my_dataset', list(range(10)))
        self.assertIsInstance(ds, DatasetBuilder)

    def test_add_group(self):
        gp = self.gb.add_group('my_subgroup')
        self.assertIsInstance(gp, GroupBuilder)

    def test_add_softlink(self):
        sl = self.gb.add_soft_link('my_softlink', '/path/to/target')
        self.assertIsInstance(sl, LinkBuilder)
        self.assertFalse(sl.hard)

    def test_add_hardlink(self):
        hl = self.gb.add_hard_link('my_hardlink', '/path/to/target')
        self.assertIsInstance(hl, LinkBuilder)
        self.assertTrue(hl.hard)

    def test_add_external_link(self):
        el = self.gb.add_external_link('my_externallink', '/path/to/target', 'external.h5')
        self.assertIsInstance(el, ExternalLinkBuilder)

    #@unittest.expectedFailure
    def test_set_attribute(self):
        self.gb.set_attribute('key', 'value')
        self.assertEqual('key' in self.gb.obj_type, True)
        self.assertEqual(dict.__getitem__(self.gb, 'attributes')['key'], 'value')

class GroupBuilderGetterTests(unittest.TestCase):

    def setUp(self):
        attrs = {
            'subgroup1': GroupBuilder(),
            'dataset1': DatasetBuilder(list(range(10))),
            'soft_link1': LinkBuilder("/soft/path/to/target"),
            'hard_link1': LinkBuilder("/hard/path/to/target", True),
            'external_link1': ExternalLinkBuilder("/hard/path/to/target",
                                                  "test.h5"),
            'int_attr': 1,
            'str_attr': "my_str",
        }
        for key, value in attrs.items():
            setattr(self, key, value)
        
        setattr(self, 'group1', GroupBuilder({'subgroup1':self.subgroup1}))
        setattr(self, 'gb', GroupBuilder({'group1': self.group1},
                                         {'dataset1': self.dataset1},
                                         {'int_attr': self.int_attr, 
                                          'str_attr': self.str_attr},
                                         {'soft_link1': self.soft_link1, 
                                          'hard_link1': self.hard_link1,
                                          'external_link1': self.external_link1}))

    def tearDown(self):
        pass

    def test_get_item_group(self):
        """Test __get_item__ for groups"""
        self.assertIs(self.gb['group1'], self.group1)

    def test_get_item_group_subgroup1(self):
        """Test __get_item__ for groups deeper in hierarchy"""
        self.assertIs(self.gb['group1/subgroup1'], self.subgroup1)

    def test_get_item_dataset(self):
        """Test __get_item__ for datasets"""
        self.assertIs(self.gb['dataset1'], self.dataset1)

    def test_get_item_attr1(self):
        """Test __get_item__ for attributes"""
        self.assertEqual(self.gb['int_attr'], self.int_attr)

    def test_get_item_attr2(self):
        """Test __get_item__ for attributes"""
        self.assertEqual(self.gb['str_attr'], self.str_attr)

    def test_get_item_invalid_key(self):
        """Test __get_item__ for invalid key"""
        with self.assertRaises(KeyError):
            self.gb['invalid_key']

    def test_get_item_soft_link(self):
        """Test __get_item__ for soft links"""
        self.assertIs(self.gb['soft_link1'], self.soft_link1)

    def test_get_item_hard_link(self):
        """Test __get_item__ for hard links"""
        self.assertIs(self.gb['hard_link1'], self.hard_link1)

    def test_get_item_external_link(self):
        """Test __get_item__ for external links"""
        self.assertIs(self.gb['external_link1'], self.external_link1)

    def test_get_group(self):
        """Test get() for groups"""
        self.assertIs(self.gb.get('group1'), self.group1)

    def test_get_group_subgroup1(self):
        """Test get() for groups deeper in hierarchy"""
        self.assertIs(self.gb.get('group1/subgroup1'), self.subgroup1)

    def test_get_dataset(self):
        """Test get() for datasets"""
        self.assertIs(self.gb.get('dataset1'), self.dataset1)

    def test_get_attr1(self):
        """Test get() for attributes"""
        self.assertEqual(self.gb.get('int_attr'), self.int_attr)

    def test_get_attr2(self):
        """Test get() for attributes"""
        self.assertEqual(self.gb.get('str_attr'), self.str_attr)

    def test_get_item_soft_link(self):
        """Test get() for soft links"""
        self.assertIs(self.gb.get('soft_link1'), self.soft_link1)

    def test_get_item_hard_link(self):
        """Test get() for hard links"""
        self.assertIs(self.gb.get('hard_link1'), self.hard_link1)

    def test_get_item_external_link(self):
        """Test get() for external links"""
        self.assertIs(self.gb.get('external_link1'), self.external_link1)

    def test_get_invalid_key(self):
        """Test get() for invalid key"""
        self.assertIs(self.gb.get('invalid_key'), None)

    def test_items(self):
        """Test items()"""
        items = (
            ('group1', self.group1),
            ('dataset1', self.dataset1),
            ('int_attr', self.int_attr),
            ('str_attr', self.str_attr),
            ('soft_link1', self.soft_link1),
            ('hard_link1', self.hard_link1),
            ('external_link1', self.external_link1)
        )
        #self.assertSetEqual(items, set(self.gb.items()))
        self.assertCountEqual(items, self.gb.items())

    def test_keys(self):
        """Test keys()"""
        keys = (
            'group1',
            'dataset1',
            'int_attr',
            'str_attr',
            'soft_link1',
            'hard_link1',
            'external_link1',
        )
        self.assertCountEqual(keys, self.gb.keys())

    def test_values(self):
        """Test values()"""
        values = (
            self.group1,
            self.dataset1,
            self.int_attr,
            self.str_attr,
            self.soft_link1,
            self.hard_link1,
            self.external_link1,
        )
        self.assertCountEqual(values, self.gb.values())

    def test_write(self):
        """Test for base dictionary functionality preservation"""
        self.maxDiff = None
        builder_json = '''
            {
            "group1": {
                "subgroup1": {
        
                }
            },
            "dataset1": {
                "attributes": {},
                "data": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9
                ]
            },
            "int_attr": 1,
            "str_attr": "my_str",
            "soft_link1": {
                "path": "/soft/path/to/target",
                "hard": false
            },
            "hard_link1": {
                "path": "/hard/path/to/target",
                "hard": true
            },
            "external_link1": {
                "path": "/hard/path/to/target",
                "file_path": "test.h5",
                "hard": false
            }
        }
        '''

        self.assertDictEqual(json.loads(builder_json), json.loads(json.dumps(self.gb)))
    

class GroupBuilderIsEmptyTests(unittest.TestCase):

    def test_is_empty_true(self):
        """Test empty when group has nothing in it"""
        gb = GroupBuilder()
        self.assertEqual(gb.is_empty(), True)

    def test_is_empty_true_group(self):
        """Test is_empty() when group has an empty subgroup"""
        gb = GroupBuilder({'my_subgroup': GroupBuilder()})
        self.assertEqual(gb.is_empty(), True)

    def test_is_empty_false_dataset(self):
        """Test is_empty() when group has a dataset"""
        gb = GroupBuilder(datasets={'my_dataset': GroupBuilder()})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_group_dataset(self):
        """Test is_empty() when group has a subgroup with a dataset"""
        gb = GroupBuilder({'my_subgroup': GroupBuilder(datasets={'my_dataset': GroupBuilder()})})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_attribute(self):
        """Test is_empty() when group has an attribute"""
        gb = GroupBuilder(attributes={'my_attr': 'attr_value'})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_group_attribute(self):
        """Test is_empty() when group has subgroup with an attribute"""
        gb = GroupBuilder({'my_subgroup': GroupBuilder(attributes={'my_attr': 'attr_value'})})
        self.assertEqual(gb.is_empty(), False)

if __name__ == '__main__':
    unittest.main()
