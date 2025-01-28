"""Tests related to pynwb.io.utils."""
import pytest

from hdmf.build import GroupBuilder
from pynwb.io.utils import get_nwb_version
from pynwb.testing import TestCase


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
