"""Tests related to pynwb.io.utils."""
import pytest

from hdmf.build import GroupBuilder
from pynwb.io.utils import get_nwb_version


def test_get_nwb_version():
    """Get the NWB version from a builder."""
    builder1 = GroupBuilder(name="root")
    builder1.set_attribute(name="nwb_version", value="2.0.0")
    builder2 = GroupBuilder(name="another")
    builder1.set_group(builder2)
    assert get_nwb_version(builder1) == (2, 0, 0)
    assert get_nwb_version(builder2) == (2, 0, 0)


def test_get_nwb_version_missing():
    """Get the NWB version from a builder where the root builder does not have an nwb_version attribute."""
    builder1 = GroupBuilder(name="root")
    builder2 = GroupBuilder(name="another")
    builder1.set_group(builder2)

    with pytest.raises(ValueError):
        get_nwb_version(builder1)

    with pytest.raises(ValueError):
        get_nwb_version(builder1)
