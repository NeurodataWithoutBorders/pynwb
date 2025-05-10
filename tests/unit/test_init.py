import os
import unittest
from platformdirs import PlatformDirs
from pynwb import __version__
from pynwb import clear_cached_typemap

@unittest.skipIf(
    os.getenv("PYNWB_NO_CACHE_DIR") == "1",
    reason="PYNWB_NO_CACHE_DIR is set to 1, skipping test"
)
def test_clear_cached_typemap():
    dirs = PlatformDirs(appname="pynwb", version=__version__, ensure_exists=True)
    cache_dir = dirs.user_cache_path
    assert (cache_dir / 'pynwb_core_typemap.pkl').exists()

    clear_cached_typemap()
    assert not (cache_dir / 'pynwb_core_typemap.pkl').exists()