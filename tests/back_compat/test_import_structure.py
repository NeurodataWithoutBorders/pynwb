from unittest import TestCase

import pynwb


class TestImportStructure(TestCase):
    """Test whether the classes/modules imported from pynwb in version 2.1.1 are still accessible.

    NOTE: this test was needed to ensure backward compatibility of "import pynwb" after changes to the package file
    hierarchy in PyNWB 2.2.0 around validate.py (see https://github.com/NeurodataWithoutBorders/pynwb/pull/1511).
    """
    def test_outer_import_structure(self):
        current_structure = dir(pynwb)
        expected_structure = [
            "BuildManager",
            "CORE_NAMESPACE",
            "DataChunkIterator",
            "H5DataIO",
            "HDMFIO",
            "NWBContainer",
            "NWBData",
            "NWBDatasetSpec",
            "NWBFile",
            "NWBGroupSpec",
            "NWBHDF5IO",
            "NWBNamespace",
            "NamespaceCatalog",
            "Path",
            "ProcessingModule",
            "TimeSeries",
            "TypeMap",
            "_HDF5IO",
            "__NS_CATALOG",
            "__TYPE_MAP",
            "__builtins__",
            "__cached__",
            "__doc__",
            "__file__",
            "__get_resources",
            "__io",
            "__loader__",
            "__name__",
            "__package__",
            "__path__",
            "__resources",
            "__spec__",
            "__version__",
            "_due",
            "_get_resources",
            "_version",
            "available_namespaces",
            "base",
            "behavior",
            "core",
            "deepcopy",
            "device",
            "docval",
            "ecephys",
            "epoch",
            "file",
            "get_class",
            "get_docval",
            "get_manager",
            "get_type_map",
            "getargs",
            "h5py",
            "hdmf",
            "hdmf_typemap",
            "icephys",
            "image",
            "io",
            "legacy",
            "load_namespaces",
            "misc",
            "ogen",
            "ophys",
            "os",
            "popargs",
            "register_class",
            "register_map",
            "spec",
            "testing",
            "validate",
        ]
        for member in expected_structure:
            self.assertIn(member=member, container=current_structure)
