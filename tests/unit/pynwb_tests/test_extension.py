import unittest
import os

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec
from pynwb import load_namespaces, get_class


class TestExtension(unittest.TestCase):

    def setUp(self):
        self.ext_source = 'fake_extension.yaml'
        self.ns_path = 'fake_namespace.yaml'

    def tearDown(self):
        os.remove(self.ext_source)
        os.remove(self.ns_path)

    def test_export(self):
        ns_builder = NWBNamespaceBuilder('Extension for us in my Lab', "mylab")
        ext1 = NWBGroupSpec('A custom ElectricalSeries for my lab',
                            attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                            neurodata_type_inc='ElectricalSeries',
                            neurodata_type_def='TetrodeSeries')
        ns_builder.add_spec(self.ext_source, ext1)
        ns_builder.export(self.ns_path)

    def test_load_namespace(self):
        self.test_export()
        load_namespaces(self.ns_path)

    def test_get_class(self):
        self.test_load_namespace()
        TetrodeSeries = get_class('TetrodeSeries', 'mylab')
