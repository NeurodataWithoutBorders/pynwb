from pathlib import Path
import tempfile
import urllib.request
from unittest import mock

from pynwb import read_nwb, NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase

import unittest
try:
    from hdmf_zarr import NWBZarrIO  # noqa f401
    HAVE_NWBZarrIO = True
except ImportError:
    HAVE_NWBZarrIO = False

try:
    import fsspec  # noqa: F401
    HAVE_FSSPEC = True
except ImportError:
    HAVE_FSSPEC = False


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

    def test_read_missing_file(self):
        """Test attempting to read a file that does not exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "does_not_exist.nwb"
            with self.assertRaisesWith(FileNotFoundError, f"Could not find the file '{path}'."):
                read_nwb(path=path)

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

    @unittest.skipIf(not HAVE_FSSPEC, "fsspec not installed")
    def test_read_nwb_anonymous_remote_hdf5(self):
        """Test reading an anonymous public HDF5 NWB file over HTTPS through fsspec."""
        url = (
            "https://dandiarchive.s3.amazonaws.com/blobs/11e/c89/"
            "11ec8933-1456-4942-922b-94e5878bb991"
        )
        try:
            urllib.request.urlopen(url, timeout=2)
        except urllib.request.URLError:
            self.skipTest("Internet access to DANDI failed.")

        nwbfile = read_nwb(path=url)
        self.assertEqual(len(nwbfile.acquisition['TestData'].data[:]), 3)
        nwbfile.get_read_io().close()

    @unittest.skipIf(not HAVE_NWBZarrIO or not HAVE_FSSPEC, "hdmf-zarr or fsspec not installed")
    def test_read_nwb_anonymous_remote_zarr(self):
        """Test reading an anonymous public Zarr NWB file from DANDI through fsspec.

        Uses the same DANDI 000719 file as hdmf-zarr's own S3 streaming tutorial (PR #330).
        Depends on hdmf-zarr's `resolve_ref` self-reference fix
        (https://github.com/hdmf-dev/hdmf-zarr/pull/348); without that fix this read
        fails with `PathNotFoundError: nothing found at path ''`.
        """
        url = (
            "https://dandiarchive.s3.amazonaws.com/zarr/"
            "c8c6b848-fbc6-4f58-85ff-e3f2618ee983/"
        )
        try:
            urllib.request.urlopen(url + ".zmetadata", timeout=2)
        except urllib.request.URLError:
            self.skipTest("Internet access to DANDI failed.")

        nwbfile = read_nwb(path=url)
        self.assertEqual(nwbfile.identifier, "7208f856-f527-479f-973d-e6e72326a8ea")
        self.assertEqual(nwbfile.subject.subject_id, "R6")
        nwbfile.get_read_io().close()

    @unittest.skipIf(not HAVE_FSSPEC, "fsspec not installed")
    def test_read_nwb_s3_scheme_uses_matching_fsspec_backend(self):
        """An ``s3://`` HDF5 URL builds the fsspec filesystem from the URL's own scheme.

        Only ``fsspec.filesystem`` is stubbed (its ``open`` returns a handle to a real
        local HDF5 file), so the dispatch, h5py read, and ``NWBHDF5IO`` read all run for
        real without network or credentials. Asserts the streaming branch passes scheme
        ``"s3"`` (not a hardcoded ``"http"``) to ``fsspec.filesystem`` and that the file
        round-trips.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.nwb"
            with NWBHDF5IO(path, 'w') as io:
                io.write(self.nwbfile)

            fake_filesystem = mock.MagicMock()
            fsspec_handle = open(path, "rb")
            fake_filesystem.open.return_value = fsspec_handle
            with mock.patch("fsspec.filesystem", return_value=fake_filesystem) as mock_filesystem:
                read_nwbfile = read_nwb(path="s3://my-bucket/test.nwb")

            mock_filesystem.assert_called_once_with("s3")
            fake_filesystem.open.assert_called_once_with("s3://my-bucket/test.nwb", "rb")
            self.assertEqual(read_nwbfile.identifier, self.nwbfile.identifier)
            self.assertEqual(read_nwbfile.session_description, self.nwbfile.session_description)
            read_nwbfile.get_read_io().close()
            # closing the IO must also close the fsspec handle, otherwise the open handle
            # leaks and, on Windows, holds a lock that blocks deletion of the file
            self.assertTrue(fsspec_handle.closed)