import unittest
import os
from tempfile import gettempdir

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec
from pynwb import load_namespaces, get_class


class TestExtension(unittest.TestCase):

    def setUp(self):
        self.tempdir = gettempdir()
        self.ext_source = 'fake_extension.yaml'
        self.ns_path = 'fake_namespace.yaml'

    def tearDown(self):
        for f in (self.ext_source, self.ns_path):
            path = os.path.join(self.tempdir, f)
            os.remove(path)

    def test_export(self):
        ns_builder = NWBNamespaceBuilder('Extension for us in my Lab', "pynwb_test_extension")
        ext1 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder.add_spec(self.ext_source, ext1)
        ns_builder.export(self.ns_path, outdir=self.tempdir)

    def test_load_namespace(self):
        self.test_export()
        load_namespaces(os.path.join(self.tempdir, self.ns_path))

    def test_get_class(self):
        self.test_load_namespace()
        TetrodeSeries = get_class('TetrodeSeries', 'pynwb_test_extension')  # noqa: F841


class TestCatchDupNS(unittest.TestCase):

    def setUp(self):
        self.tempdir = gettempdir()
        self.ext_source1 = 'fake_extension1.yaml'
        self.ns_path1 = 'fake_namespace1.yaml'
        self.ext_source2 = 'fake_extension2.yaml'
        self.ns_path2 = 'fake_namespace2.yaml'

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
                            attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder1.add_spec(self.ext_source1, ext1)
        ns_builder1.export(self.ns_path1, outdir=self.tempdir)
        ns_builder2 = NWBNamespaceBuilder('Extension for us in my Lab', "pynwb_test_extension1")
        ext2 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder2.add_spec(self.ext_source2, ext2)
        ns_builder2.export(self.ns_path2, outdir=self.tempdir)
        load_namespaces(os.path.join(self.tempdir, self.ns_path1))
        with self.assertRaises(KeyError):
            load_namespaces(os.path.join(self.tempdir, self.ns_path2))


class TestCatchDuplicateSpec(unittest.TestCase):

    def setUp(self):
        self.ext_source = 'fake_extension3.yaml'

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
