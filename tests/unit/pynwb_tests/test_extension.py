import unittest2 as unittest
import os
from tempfile import gettempdir
import random
import string

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBDatasetSpec
from pynwb.form.spec.spec import RefSpec
from pynwb import get_type_map, TimeSeries
from pynwb.form.utils import get_docval


def id_generator(N=10):
    """
    Generator a random string of characters.
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


class TestExtension(unittest.TestCase):

    def setUp(self):
        self.tempdir = gettempdir()
        self.prefix = id_generator()
        self.ext_source = '%s_extension.yaml' % self.prefix
        self.ns_path = '%s_namespace.yaml' % self.prefix

    def tearDown(self):
        for f in (self.ext_source, self.ns_path):
            path = os.path.join(self.tempdir, f)
            os.remove(path)

    def test_export(self):
        ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', self.prefix)
        ext1 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec(name='trode_id', doc='the tetrode id', dtype='int')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder.add_spec(self.ext_source, ext1)
        ns_builder.export(self.ns_path, outdir=self.tempdir)

    def test_load_namespace(self):
        self.test_export()
        get_type_map(extensions=os.path.join(self.tempdir, self.ns_path))

    def test_get_class(self):
        self.test_export()
        type_map = get_type_map(extensions=os.path.join(self.tempdir, self.ns_path))
        type_map.get_container_cls(self.prefix, 'TetrodeSeries')

    def test_load_namespace_with_reftype_attribute(self):
        ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', self.prefix)
        test_ds_ext = NWBDatasetSpec(doc='test dataset to add an attr',
                                     name='test_data', shape=(None,),
                                     attributes=[NWBAttributeSpec(name='target_ds',
                                                                  doc='the target the dataset applies to',
                                                                  dtype=RefSpec('TimeSeries', 'object'))],
                                     neurodata_type_def='my_new_type')
        ns_builder.add_spec(self.ext_source, test_ds_ext)
        ns_builder.export(self.ns_path, outdir=self.tempdir)
        get_type_map(extensions=os.path.join(self.tempdir, self.ns_path))

    def test_load_namespace_with_reftype_attribute_check_autoclass_const(self):
        ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', self.prefix)
        test_ds_ext = NWBDatasetSpec(doc='test dataset to add an attr',
                                     name='test_data', shape=(None,),
                                     attributes=[NWBAttributeSpec(name='target_ds',
                                                                  doc='the target the dataset applies to',
                                                                  dtype=RefSpec('TimeSeries', 'object'))],
                                     neurodata_type_def='my_new_type')
        ns_builder.add_spec(self.ext_source, test_ds_ext)
        ns_builder.export(self.ns_path, outdir=self.tempdir)
        type_map = get_type_map(extensions=os.path.join(self.tempdir, self.ns_path))
        my_new_type = type_map.get_container_cls(self.prefix, 'my_new_type')
        docval = None
        for tmp in get_docval(my_new_type.__init__):
            if tmp['name'] == 'target_ds':
                docval = tmp
                break
        self.assertIsNotNone(docval)
        self.assertEqual(docval['type'], TimeSeries)


class TestCatchDupNS(unittest.TestCase):

    def setUp(self):
        self.tempdir = gettempdir()
        self.prefix = id_generator()
        self.ext_source1 = '%s_extension1.yaml' % self.prefix
        self.ns_path1 = '%s_namespace1.yaml' % self.prefix
        self.ext_source2 = '%s_extension2.yaml' % self.prefix
        self.ns_path2 = '%s_namespace2.yaml' % self.prefix

    def tearDown(self):
        files = (self.ext_source1,
                 self.ns_path1,
                 self.ext_source2,
                 self.ns_path2)
        for f in files:
            path = os.path.join(self.tempdir, f)
            os.remove(path)

    def test_catch_dup_name(self):
        ns_builder1 = NWBNamespaceBuilder('Extension for us in my Lab', "pynwb_test_extension1")
        ext1 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec(name='trode_id', doc='the tetrode id', dtype='int')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder1.add_spec(self.ext_source1, ext1)
        ns_builder1.export(self.ns_path1, outdir=self.tempdir)
        ns_builder2 = NWBNamespaceBuilder('Extension for us in my Lab', "pynwb_test_extension1")
        ext2 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec(name='trode_id', doc='the tetrode id', dtype='int')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder2.add_spec(self.ext_source2, ext2)
        ns_builder2.export(self.ns_path2, outdir=self.tempdir)
        type_map = get_type_map(extensions=os.path.join(self.tempdir, self.ns_path1))
        with self.assertWarnsRegex(UserWarning, r"ignoring namespace '\S+' because it already exists"):
            type_map.load_namespaces(os.path.join(self.tempdir, self.ns_path2))


class TestCatchDuplicateSpec(unittest.TestCase):

    def setUp(self):
        self.prefix = id_generator()
        self.ext_source = '%s_extension3.yaml' % self.prefix

    def tearDown(self):
        pass

    def test_catch_duplicate_spec(self):
        spec1 = NWBGroupSpec("This is my new group 1",
                             "Group1",
                             neurodata_type_inc="NWBDataInterface",
                             neurodata_type_def="Group1")
        spec2 = NWBGroupSpec("This is my new group 2",
                             "Group2",
                             groups=[spec1],
                             neurodata_type_inc="NWBDataInterface",
                             neurodata_type_def="Group2")
        ns_builder = NWBNamespaceBuilder("Example namespace",
                                         "pynwb_test_ext")
        ns_builder.add_spec(self.ext_source, spec1)
        with self.assertRaises(ValueError):
            ns_builder.add_spec(self.ext_source, spec2)
