import sys
from unittest import TestCase

import pynwb


class TestImportStructure(TestCase):
    maxDiff = None
    original_import_structure_outer_level = [
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
        "ValidatorMap",
        "_HDF5IO",
        "__NS_CATALOG",
        "__TYPE_MAP",
        "__builtins__",
        "__cached__",
        "__core_ns_file_name",
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
        "call_docval_func",
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
        "retinotopy",
        "spec",
        "validate",
        "warn",
    ]

    def test_outer_level_import_backcompatability(self):
        full_new_import_structure = [x for x in sys.modules["pynwb"].__dict__]
        exclude_names = ["globals", "utils", "validation"]  # new ones being introduced

        overlap_structure = [x for x in full_new_import_structure if x not in exclude_names]

        self.assertCountEqual(first=self.original_import_structure_outer_level, second=overlap_structure)
