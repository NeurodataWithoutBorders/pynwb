import subprocess
import re

from pynwb.testing import TestCase
from pynwb import validate, NWBHDF5IO


class TestValidateScript(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specifications

    def test_validate_file_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.0.2_nwbfile.nwb",
                                capture_output=True)

        stderr_regex = re.compile(
            r".*UserWarning: No cached namespaces found in tests/back_compat/1\.0\.2_nwbfile\.nwb\s*"
            r"warnings.warn\(msg\)\s*"
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to pynwb namespace information\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.0\.2_nwbfile\.nwb against pynwb namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.0.2_nwbfile.nwb --ns notfound",
                                capture_output=True)

        stderr_regex = re.compile(
            r".*UserWarning: No cached namespaces found in tests/back_compat/1\.0\.2_nwbfile\.nwb\s*"
            r"warnings.warn\(msg\)\s*"
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to pynwb namespace information\.\s*"
            r"The namespace 'notfound' could not be found in pynwb namespace information\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.1.2_nwbfile.nwb",
                                capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against cached namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_bad_ns(self):
        """Test that validating a file with cached spec against a specified, unknown namespace fails."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.1.2_nwbfile.nwb --ns notfound",
                                capture_output=True)

        stderr_regex = re.compile(
            r"The namespace 'notfound' could not be found in cached namespace information\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.1.2_nwbfile.nwb --ns hdmf-common",
                                capture_output=True)

        stderr_regex = re.compile(
            r".*ValueError: data type \'NWBFile\' not found in namespace hdmf-common.\s*",
            re.DOTALL
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1.1.2_nwbfile.nwb against cached namespace information using namespace "
            r"'hdmf-common'.\s*"
        )
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_ignore(self):
        """Test that validating a file with cached spec against the core namespace succeeds."""
        result = subprocess.run("python -m pynwb.validate tests/back_compat/1.1.2_nwbfile.nwb --no-cached-namespace",
                                capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against pynwb namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)


class TestValidateFunction(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specifications

    def test_validate_file_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        with NWBHDF5IO('tests/back_compat/1.0.2_nwbfile.nwb', 'r') as io:
            errors = validate(io)
            self.assertEqual(errors, [])

    def test_validate_file_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.0.2_nwbfile.nwb', 'r') as io:
            with self.assertRaisesWith(KeyError, "\"'notfound' not a namespace\""):
                validate(io, 'notfound')

    def test_validate_file_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            errors = validate(io)
            self.assertEqual(errors, [])

    def test_validate_file_cached_bad_ns(self):
        """Test that validating a file with cached spec against a specified, unknown namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            with self.assertRaisesWith(KeyError, "\"'notfound' not a namespace\""):
                validate(io, 'notfound')

    def test_validate_file_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            # TODO this error should not be different from the error when using the validate script above
            msg = "builder must have data type defined with attribute 'data_type'"
            with self.assertRaisesWith(ValueError, msg):
                validate(io, 'hdmf-common')
