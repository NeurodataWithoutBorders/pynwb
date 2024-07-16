"""
Test functionality of import-time functionality like loading the core
namespace and cloning the submodules and whatnot
"""
import importlib
import tempfile
import shutil
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from pynwb.testing import TestCase

class TestPyNWBSubmoduleClone(TestCase):
    def setUp(self):
        # move the existing cloned submodules to a temporary directory
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo_dir: Path = files('pynwb') / 'nwb-schema'
        if self.repo_dir.exists():
            shutil.move(self.repo_dir, self.tmp_dir.name)

        # remove cache files if they exist
        self.typemap_cache = Path(files('pynwb') / 'core_typemap.pkl')
        self.nscatalog_cache = Path(files('pynwb') / 'core_nscatalog.pkl')
        self.typemap_cache.unlink(missing_ok=True)
        self.nscatalog_cache.unlink(missing_ok=True)


    def tearDown(self) -> None:
        # move the old repository back
        if self.repo_dir.exists():
            shutil.rmtree(self.repo_dir)
            shutil.move(Path(self.tmp_dir.name) / 'nwb-schema', self.repo_dir)

    def test_clone_on_import(self):
        """
        On import, if the schema directory is not found,
        we should try and import it
        """
        assert not self.repo_dir.exists()
        assert not self.nscatalog_cache.exists()
        assert not self.typemap_cache.exists()

        with self.assertWarns(Warning) as clone_warning:
            import pynwb
            importlib.reload(pynwb)

            # there can be other warnings, but we should get at least one
            assert len(clone_warning.warnings) > 0
            messages = [str(warn.message) for warn in clone_warning.warnings]
            assert any(['initializing submodules' in msg for msg in messages])

        assert self.repo_dir.exists()
        assert self.nscatalog_cache.exists()
        assert self.typemap_cache.exists()

        # we should also get the namespaces correctly too
        assert 'core' in pynwb.available_namespaces()


class TestPyNWBImportCache(TestCase):
    def setUp(self) -> None:
        self.typemap_cache = Path(files('pynwb') / 'core_typemap.pkl')

    def test_cache_exists(self):
        assert self.typemap_cache.exists()

    def test_typemap_ns_match(self):
        """
        The global __NS_CATALOG and the one contained within the global __TYPE_MAP
        should be the same object after importing
        """
        import pynwb
        assert id(pynwb.__TYPE_MAP.namespace_catalog) == id(pynwb.__NS_CATALOG)