"""Tests related to pynwb.io.utils."""
import pytest

from datetime import datetime
from dateutil.tz import tzutc

from hdmf.build import GroupBuilder
from pynwb.io.utils import get_nwb_version
from pynwb.testing import TestCase, remove_test_file
from pynwb import NWBFile, NWBHDF5IO, _get_backend

class TestGetNWBVersion(TestCase):

    def test_get_nwb_version(self):
        """Get the NWB version from a builder."""
        builder1 = GroupBuilder(name="root")
        builder1.set_attribute(name="nwb_version", value="2.0.0")
        builder2 = GroupBuilder(name="another")
        builder1.set_group(builder2)
        assert get_nwb_version(builder1) == (2, 0, 0)
        assert get_nwb_version(builder2) == (2, 0, 0)

    def test_get_nwb_version_missing(self):
        """Get the NWB version from a builder where the root builder does not have an nwb_version attribute."""
        builder1 = GroupBuilder(name="root")
        builder2 = GroupBuilder(name="another")
        builder1.set_group(builder2)

        with pytest.raises(ValueError, match="'nwb_version' attribute is missing from the root of the NWB file."):
            get_nwb_version(builder1)

        with pytest.raises(ValueError, match="'nwb_version' attribute is missing from the root of the NWB file."):
            get_nwb_version(builder1)

    def test_get_nwb_version_prerelease_false(self):
        """Get the NWB version from a builder."""
        builder1 = GroupBuilder(name="root")
        builder1.set_attribute(name="nwb_version", value="2.0.0-alpha")
        assert get_nwb_version(builder1) == (2, 0, 0)

    def test_get_nwb_version_prerelease_true1(self):
        """Get the NWB version from a builder."""
        builder1 = GroupBuilder(name="root")
        builder1.set_attribute(name="nwb_version", value="2.0.0-alpha")
        assert get_nwb_version(builder1, include_prerelease=True) == (2, 0, 0, "alpha")

    def test_get_nwb_version_prerelease_true2(self):
        """Get the NWB version from a builder."""
        builder1 = GroupBuilder(name="root")
        builder1.set_attribute(name="nwb_version", value="2.0.0-alpha.sha-test.5114f85")
        assert get_nwb_version(builder1, include_prerelease=True) == (2, 0, 0, "alpha.sha-test.5114f85")

    def test_get_nwb_version_20b(self):
        """Get the NWB version from a builder where version == "2.0b"."""
        builder1 = GroupBuilder(name="root")
        builder1.set_attribute(name="nwb_version", value="2.0b")
        assert get_nwb_version(builder1) == (2, 0, 0)
        assert get_nwb_version(builder1, include_prerelease=True) == (2, 0, 0, "b")

class TestGetNWBBackend(TestCase):
    def setUp(self):
        self.nwbfile = NWBFile(session_description='a test NWB File',
                               identifier='TEST123',
                               session_start_time=datetime(1970, 1, 1, 12, tzinfo=tzutc()))
        self.hdf5_path = "test_pynwb_nwb_backend.nwb"
        with NWBHDF5IO(self.hdf5_path, 'w') as io:
            io.write(self.nwbfile)

    def tearDown(self):
        remove_test_file(self.hdf5_path)

    def test_get_backend_invalid_file(self):
        with self.assertRaises(ValueError):
            _get_backend('not_a_file.nwb')

    def test_get_backend_HDF5(self):
        backend_io = _get_backend(self.hdf5_path)
        self.assertEqual(backend_io, NWBHDF5IO)