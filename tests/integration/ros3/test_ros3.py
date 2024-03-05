from pynwb import NWBHDF5IO
from pynwb import validate
from pynwb.validate import _get_cached_namespaces_to_validate
from pynwb.testing import TestCase
import urllib.request
import h5py
import warnings


class TestRos3Streaming(TestCase):
    """
    Test file access using the HDF5 ros3 driver.

    This test module requires h5py to be built with the ROS3 driver: conda install -c conda-forge h5py
    """
    @classmethod
    def setUpClass(cls):
        # this is the NWB Test Data dandiset #000126 sub-1/sub-1.nwb
        cls.s3_test_path = "https://dandiarchive.s3.amazonaws.com/blobs/11e/c89/11ec8933-1456-4942-922b-94e5878bb991"

    def setUp(self):
        # Skip ROS3 tests if internet is not available or the ROS3 driver is not installed
        try:
            urllib.request.urlopen('https://dandiarchive.s3.amazonaws.com/ros3test.nwb', timeout=1)
        except urllib.request.URLError:
            self.skipTest("Internet access to DANDI failed. Skipping all Ros3 streaming tests.")
        if 'ros3' not in h5py.registered_drivers():
            self.skipTest("ROS3 driver not installed. Skipping all Ros3 streaming tests.")

    def test_read(self):
        s3_path = 'https://dandiarchive.s3.amazonaws.com/ros3test.nwb'
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Ignoring cached namespace .*",
                category=UserWarning,
            )
            with NWBHDF5IO(s3_path, mode='r', driver='ros3') as io:
                nwbfile = io.read()
                test_data = nwbfile.acquisition['ts_name'].data[:]
                self.assertEqual(len(test_data), 3)

    def test_dandi_read(self):
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Ignoring cached namespace .*",
                category=UserWarning,
            )
            with NWBHDF5IO(path=self.s3_test_path, mode='r', driver='ros3') as io:
                nwbfile = io.read()
                test_data = nwbfile.acquisition['TestData'].data[:]
                self.assertEqual(len(test_data), 3)

    def test_dandi_get_cached_namespaces(self):
        expected_namespaces = ["core"]
        expected_namespace_dependencies = {
            'core': {
                'hdmf-common': (
                    'AlignedDynamicTable',
                    'CSRMatrix',
                    'Container',
                    'Data',
                    'DynamicTable',
                    'DynamicTableRegion',
                    'ElementIdentifiers',
                    'SimpleMultiContainer',
                    'VectorData',
                    'VectorIndex'
                )
            },
            'hdmf-common': {},
            'hdmf-experimental': {
                'hdmf-common': (
                    'AlignedDynamicTable',
                    'CSRMatrix',
                    'Container',
                    'Data',
                    'DynamicTable',
                    'DynamicTableRegion',
                    'ElementIdentifiers',
                    'SimpleMultiContainer',
                    'VectorData',
                    'VectorIndex'
                )
            }
        }
        found_namespaces, _, found_namespace_dependencies = _get_cached_namespaces_to_validate(
            path=self.s3_test_path, driver="ros3"
        )

        self.assertCountEqual(first=found_namespaces, second=expected_namespaces)
        self.assertDictEqual(d1=expected_namespace_dependencies, d2=expected_namespace_dependencies)

    def test_dandi_validate(self):
        result, status = validate(paths=[self.s3_test_path], driver="ros3")

        assert result == []
        assert status == 0
