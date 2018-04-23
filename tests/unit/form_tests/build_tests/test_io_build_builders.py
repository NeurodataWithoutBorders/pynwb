import unittest2 as unittest

from pynwb.form.build import GroupBuilder, DatasetBuilder, LinkBuilder


class GroupBuilderSetterTests(unittest.TestCase):
    """Tests for setter functions in GroupBuilder class"""

    def setUp(self):
        self.gb = GroupBuilder('gb')
        self.gb2 = GroupBuilder('gb2', source='file1')

    def tearDown(self):
        pass

    def test_setitem_disabled(self):
        """Test __set_item__ is disabled"""
        with self.assertRaises(NotImplementedError):
            self.gb['key'] = 'value'

    def test_add_dataset(self):
        ds = self.gb.add_dataset('my_dataset', list(range(10)))
        self.assertIsInstance(ds, DatasetBuilder)
        self.assertIs(self.gb, ds.parent)

    def test_add_group(self):
        gp = self.gb.add_group('my_subgroup')
        self.assertIsInstance(gp, GroupBuilder)
        self.assertIs(self.gb['my_subgroup'], gp)
        self.assertIs(self.gb, gp.parent)

    def test_add_link(self):
        gp = self.gb.add_group('my_subgroup')
        sl = self.gb.add_link(gp, 'my_link')
        self.assertIsInstance(sl, LinkBuilder)
        self.assertIs(self.gb['my_link'], sl)
        self.assertIs(self.gb, sl.parent)

    def test_add_external_link(self):
        gp = self.gb2.add_group('my_subgroup')
        el = self.gb.add_link(gp, 'my_externallink')
        self.assertIsInstance(el, LinkBuilder)
        self.assertIs(self.gb['my_externallink'], el)
        self.assertIs(self.gb, el.parent)
        self.assertIs(self.gb2, gp.parent)

    # @unittest.expectedFailure
    def test_set_attribute(self):
        self.gb.set_attribute('key', 'value')
        self.assertIn('key', self.gb.obj_type)
        # self.assertEqual(dict.__getitem__(self.gb, 'attributes')['key'], 'value')
        self.assertEqual(self.gb['key'], 'value')

    def test_parent_constructor(self):
        gb2 = GroupBuilder('gb2', parent=self.gb)
        self.assertIs(gb2.parent, self.gb)

    def test_set_group(self):
        self.gb.set_group(self.gb2)
        self.assertIs(self.gb2.parent, self.gb)


class GroupBuilderGetterTests(unittest.TestCase):

    def setUp(self):
        self.subgroup1 = GroupBuilder('subgroup1')
        self.dataset1 = DatasetBuilder('dataset1', list(range(10)))
        self.soft_link1 = LinkBuilder(self.subgroup1, 'soft_link1')
        self.int_attr = 1
        self.str_attr = "my_str"

        self.group1 = GroupBuilder('group1', {'subgroup1': self.subgroup1})
        self.gb = GroupBuilder('gb', {'group1': self.group1},
                               {'dataset1': self.dataset1},
                               {'int_attr': self.int_attr,
                                'str_attr': self.str_attr},
                               {'soft_link1': self.soft_link1})
        # {'soft_link1': self.soft_link1,
        #  'external_link1': self.external_link1}))

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

    def test_get_item_soft_link(self):  # noqa: F811
        """Test get() for soft links"""
        self.assertIs(self.gb.get('soft_link1'), self.soft_link1)

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
            # ('external_link1', self.external_link1)
        )
        # self.assertSetEqual(items, set(self.gb.items()))
        try:
            self.assertCountEqual(items, self.gb.items())
        except AttributeError:
            self.assertItemsEqual(items, self.gb.items())

    def test_keys(self):
        """Test keys()"""
        keys = (
            'group1',
            'dataset1',
            'int_attr',
            'str_attr',
            'soft_link1',
            # 'external_link1',
        )
        try:
            self.assertCountEqual(keys, self.gb.keys())
        except AttributeError:
            self.assertItemsEqual(keys, self.gb.keys())

    def test_values(self):
        """Test values()"""
        values = (
            self.group1,
            self.dataset1,
            self.int_attr, self.str_attr,
            self.soft_link1,
            # self.external_link1,
        )
        try:
            self.assertCountEqual(values, self.gb.values())
        except AttributeError:
            self.assertItemsEqual(values, self.gb.values())


class GroupBuilderIsEmptyTests(unittest.TestCase):

    def test_is_empty_true(self):
        """Test empty when group has nothing in it"""
        gb = GroupBuilder('gb')
        self.assertEqual(gb.is_empty(), True)

    def test_is_empty_true_group(self):
        """Test is_empty() when group has an empty subgroup"""
        gb = GroupBuilder('gb', {'my_subgroup': GroupBuilder('my_subgroup')})
        self.assertEqual(gb.is_empty(), True)

    def test_is_empty_false_dataset(self):
        """Test is_empty() when group has a dataset"""
        gb = GroupBuilder('gb', datasets={'my_dataset': DatasetBuilder('my_dataset')})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_group_dataset(self):
        """Test is_empty() when group has a subgroup with a dataset"""
        gb = GroupBuilder(
            'gb',
            {'my_subgroup':
             GroupBuilder(
                 'my_subgroup',
                 datasets={'my_dataset': DatasetBuilder('my_dataset')})})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_attribute(self):
        """Test is_empty() when group has an attribute"""
        gb = GroupBuilder('gb', attributes={'my_attr': 'attr_value'})
        self.assertEqual(gb.is_empty(), False)

    def test_is_empty_false_group_attribute(self):
        """Test is_empty() when group has subgroup with an attribute"""
        gb = GroupBuilder('gb', {'my_subgroup': GroupBuilder('my_subgroup', attributes={'my_attr': 'attr_value'})})
        self.assertEqual(gb.is_empty(), False)


class GroupBuilderDeepUpdateTests(unittest.TestCase):

    def test_mutually_exclusive_subgroups(self):
        gb1 = GroupBuilder('gb1', {'subgroup1': GroupBuilder('subgroup1')})
        gb2 = GroupBuilder('gb2', {'subgroup2': GroupBuilder('subgroup2')})
        gb1.deep_update(gb2)
        self.assertIn('subgroup2', gb1)
        gb1sg = gb1['subgroup2']
        gb2sg = gb2['subgroup2']
        self.assertIs(gb1sg, gb2sg)

    def test_mutually_exclusive_datasets(self):
        gb1 = GroupBuilder('gb1', datasets={'dataset1': DatasetBuilder('dataset1', [1, 2, 3])})
        gb2 = GroupBuilder('gb2', datasets={'dataset2': DatasetBuilder('dataset2', [4, 5, 6])})
        gb1.deep_update(gb2)
        self.assertIn('dataset2', gb1)
        # self.assertIs(gb1['dataset2'], gb2['dataset2'])
        self.assertListEqual(gb1['dataset2'].data, gb2['dataset2'].data)

    def test_mutually_exclusive_attributes(self):
        gb1 = GroupBuilder('gb1', attributes={'attr1': 'my_attribute1'})
        gb2 = GroupBuilder('gb2', attributes={'attr2': 'my_attribute2'})
        gb1.deep_update(gb2)
        self.assertIn('attr2', gb2)
        self.assertEqual(gb2['attr2'], 'my_attribute2')

    def test_mutually_exclusive_links(self):
        gb1 = GroupBuilder('gb1', links={'link1': LinkBuilder(GroupBuilder('target1'), 'link1')})
        gb2 = GroupBuilder('gb2', links={'link2': LinkBuilder(GroupBuilder('target2'), 'link2')})
        gb1.deep_update(gb2)
        self.assertIn('link2', gb2)
        self.assertEqual(gb1['link2'], gb2['link2'])

    def test_intersecting_subgroups(self):
        subgroup2 = GroupBuilder('subgroup2')
        gb1 = GroupBuilder('gb1', {'subgroup1': GroupBuilder('subgroup1'), 'subgroup2': subgroup2})
        gb2 = GroupBuilder('gb2', {'subgroup2': GroupBuilder('subgroup2'), 'subgroup3': GroupBuilder('subgroup3')})
        gb1.deep_update(gb2)
        self.assertIn('subgroup3', gb1)
        self.assertIs(gb1['subgroup3'], gb2['subgroup3'])
        self.assertIs(gb1['subgroup2'], subgroup2)

    def test_intersecting_datasets(self):
        gb1 = GroupBuilder('gb1', datasets={'dataset2': DatasetBuilder('dataset2', [1, 2, 3])})
        gb2 = GroupBuilder('gb2', datasets={'dataset2': DatasetBuilder('dataset2', [4, 5, 6])})
        gb1.deep_update(gb2)
        self.assertIn('dataset2', gb1)
        self.assertListEqual(gb1['dataset2'].data, gb2['dataset2'].data)

    def test_intersecting_attributes(self):
        gb1 = GroupBuilder('gb1', attributes={'attr2': 'my_attribute1'})
        gb2 = GroupBuilder('gb2', attributes={'attr2': 'my_attribute2'})
        gb1.deep_update(gb2)
        self.assertIn('attr2', gb2)
        self.assertEqual(gb2['attr2'], 'my_attribute2')

    def test_intersecting_links(self):
        gb1 = GroupBuilder('gb1', links={'link2': LinkBuilder(GroupBuilder('target1'), 'link2')})
        gb2 = GroupBuilder('gb2', links={'link2': LinkBuilder(GroupBuilder('target2'), 'link2')})
        gb1.deep_update(gb2)
        self.assertIn('link2', gb2)
        self.assertEqual(gb1['link2'], gb2['link2'])


class DatasetBuilderDeepUpdateTests(unittest.TestCase):

    def test_overwrite(self):
        db1 = DatasetBuilder('db1', [1, 2, 3])
        db2 = DatasetBuilder('db2', [4, 5, 6])
        db1.deep_update(db2)
        self.assertListEqual(db1.data, db2.data)

    def test_no_overwrite(self):
        db1 = DatasetBuilder('db1', [1, 2, 3])
        db2 = DatasetBuilder('db2', [4, 5, 6], attributes={'attr1': 'va1'})
        db1.deep_update(db2)
        self.assertListEqual(db1.data, db2.data)
        self.assertIn('attr1', db1.attributes)


if __name__ == '__main__':
    unittest.main()
