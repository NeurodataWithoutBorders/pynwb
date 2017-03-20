import unittest

from pynwb.io.tools import H5Builder, TypeMap, SpecCatalog



class TestIO(unittest.TestCase):

    def setUp(self):
        self.spec_catalog = SpecCatalog()
        self.type_map = TypeMap(self.spec_catalog)

    def test_typemap(self):
        self.assertTrue(True)
        @self.type_map.neurodata_type('SomeType')
        class SomeTypeMap(H5Builder):
            pass
