import os
import tempfile
import pynwb
import unittest
from pathlib import Path
from unittest.mock import patch


class TestTypemapCache(unittest.TestCase):
    """Tests for the typemap caching functionality."""

    def setUp(self):
        """Set up a temporary directory for cache files."""

        # create mock resources variables for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_resources = getattr(pynwb, '__resources')
        self.mock_resources = dict(
            namespace_path=self.original_resources['namespace_path'],
            user_cache_dir=Path(self.temp_dir.name) / "pynwb" / pynwb.__version__,
            cached_typemap_path=Path(self.temp_dir.name) / "pynwb" / pynwb.__version__ / 'pynwb_core_typemap.pkl',
        )

        # make the cache directories if they do not exist
        Path(self.mock_resources['user_cache_dir']).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directory and restore environment."""
        self.temp_dir.cleanup()

    @patch.dict(os.environ, {'PYNWB_NO_CACHE_DIR': '1'})
    def test_typemap_cache_disabled(self):
        """Test that caching is disabled when environment variable is set."""
        with patch.object(pynwb, '__resources', self.mock_resources):
            # Remove any existing cache files before we start, make the cache_dir
            cache_path = Path(self.mock_resources['cached_typemap_path'])
            cache_path.unlink(missing_ok=True)

            # Force a reload of the core namespace
            load_func = getattr(pynwb, '__load_core_namespace')
            load_func()

            # Verify the cache file was not created
            self.assertFalse(cache_path.exists())

    @patch.dict(os.environ, {'PYNWB_NO_CACHE_DIR': '0'})
    def test_typemap_cache_error_handling(self):
        """Test error handling when encountering write errors to cache directory"""
        with patch.object(pynwb, '__resources', self.mock_resources):
            # Remove any existing cache file
            cache_path = Path(self.mock_resources['cached_typemap_path'])
            cache_path.unlink(missing_ok=True)

            # Mock open to raise a permission error when trying to write
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                load_func = getattr(pynwb, '__load_core_namespace')
                load_func()

            # check that cache file was not written
            self.assertFalse(cache_path.exists())
