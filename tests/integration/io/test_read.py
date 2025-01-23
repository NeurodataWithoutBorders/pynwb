from pathlib import Path
import tempfile

from pynwb import read_nwb
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase

import unittest
try:
    from hdmf_zarr import NWBZarrIO  # noqa f401
    HAVE_NWBZarrIO = True 
except ImportError:
    HAVE_NWBZarrIO = False


class TestReadNWBMethod(TestCase):
    """Test suite for the read_nwb function."""
    
    def setUp(self):
        self.nwbfile = mock_NWBFile()

    def test_read_nwb_hdf5(self):
        """Test reading a valid HDF5 NWB file."""
        from pynwb import NWBHDF5IO
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.nwb"
            with NWBHDF5IO(path, 'w') as io:
                io.write(self.nwbfile)
            
            read_nwbfile = read_nwb(path=path)
            self.assertContainerEqual(read_nwbfile, self.nwbfile)
            read_nwbfile.get_read_io().close()
            
    @unittest.skipIf(not HAVE_NWBZarrIO, "NWBZarrIO library not available")
    def test_read_zarr(self):
        """Test reading a valid Zarr NWB file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.zarr"
            with NWBZarrIO(path, 'w') as io:
                io.write(self.nwbfile)
            
            read_nwbfile = read_nwb(path=path)
            self.assertContainerEqual(read_nwbfile, self.nwbfile)
            read_nwbfile.get_read_io().close()

    def test_read_zarr_without_hdmf_zarr(self):
        """Test attempting to read a Zarr file without hdmf_zarr installed."""
        if HAVE_NWBZarrIO:
            self.skipTest("hdmf_zarr is installed")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.zarr"
            path.mkdir()  # Create empty directory to simulate Zarr store

            expected_message = (
                f"Unable to read file: '{path}'. The file is not recognized as an HDF5 NWB file. "
                "If you are trying to read a Zarr file, please install hdmf-zarr using: pip install hdmf-zarr"
            )

            with self.assertRaisesWith(ValueError, expected_message):
                read_nwb(path=path)
        
    @unittest.skipIf(not HAVE_NWBZarrIO, "NWBZarrIO library not available. Need for correct error message.")
    def test_read_invalid_file(self):
        """Test attempting to read a file that exists but is neither HDF5 nor Zarr."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.txt"
            path.write_text("Not an NWB file")
            
            expected_message = (
                f"Unable to read file: '{path}'. The file is not recognized as either a valid HDF5 or Zarr NWB file. "
                "Please ensure the file exists and contains valid NWB data."
            )
            
            with self.assertRaisesWith(ValueError, expected_message):
                read_nwb(path=path)