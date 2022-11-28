import subprocess
import re
from unittest.mock import patch
from io import StringIO

from pynwb.testing import TestCase
from pynwb import validate, NWBHDF5IO


class TestValidateCLI(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specifications

    # NOTE we use "coverage run -m pynwb.validate" instead of "python -m pynwb.validate"
    # so that we can both test pynwb.validate and compute code coverage from that test.
    # NOTE we also use "coverage run -p" which will generate a .coverage file with the
    # machine name, process id, and a random number appended to the filename to
    # simplify collecting and merging coverage data from multiple subprocesses. if "-p"
    # is not used, then each "coverage run" will overwrite the .coverage file from a
    # previous "coverage run".
    # NOTE the run_coverage.yml GitHub Action runs "python -m coverage combine" to
    # combine the individual coverage reprots into one .coverage file.

    def test_validate_file_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/1.0.2_nwbfile.nwb"], capture_output=True)

        stderr_regex = re.compile(
            r".*UserWarning: No cached namespaces found in tests/back_compat/1\.0\.2_nwbfile\.nwb\s*"
            r"warnings.warn\(msg\)\s*"
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to PyNWB namespace information\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.0\.2_nwbfile\.nwb against PyNWB namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/1.0.2_nwbfile.nwb",
                                 "--ns", "notfound"], capture_output=True)

        stderr_regex = re.compile(
            r".*UserWarning: No cached namespaces found in tests/back_compat/1\.0\.2_nwbfile\.nwb\s*"
            r"warnings.warn\(msg\)\s*"
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to PyNWB namespace information\.\s*"
            r"The namespace 'notfound' could not be found in PyNWB namespace information as only "
            r"\['core'\] is present\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/1.1.2_nwbfile.nwb"], capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against cached namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_bad_ns(self):
        """Test that validating a file with cached spec against a specified, unknown namespace fails."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/1.1.2_nwbfile.nwb", "--ns", "notfound"], capture_output=True)

        stderr_regex = re.compile(
            r"The namespace 'notfound' could not be found in cached namespace information as only "
            r"\['core'\] is present\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached_extension(self):
        """Test that validating a file with cached spec against the cached namespaces succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/2.1.0_nwbfile_with_extension.nwb"], capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/2\.1\.0_nwbfile_with_extension\.nwb against cached namespace information "
            r"using namespace 'ndx-testextension'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_extension_pass_ns(self):
        """Test that validating a file with cached spec against the extension namespace succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/2.1.0_nwbfile_with_extension.nwb",
                                 "--ns", "ndx-testextension"], capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/2\.1\.0_nwbfile_with_extension\.nwb against cached namespace information "
            r"using namespace 'ndx-testextension'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_core(self):
        """Test that validating a file with cached spec against the core namespace succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate",
                                 "tests/back_compat/2.1.0_nwbfile_with_extension.nwb",
                                 "--ns", "core"], capture_output=True)

        stdout_regex = re.compile(
            r"The namespace 'core' is included by the namespace 'ndx-testextension'. "
            r"Please validate against that namespace instead\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/1.1.2_nwbfile.nwb",
                                 "--ns", "hdmf-common"], capture_output=True)

        stderr_regex = re.compile(
            r"The namespace 'hdmf-common' is included by the namespace 'core'\. Please validate against that "
            r"namespace instead\.\s*",
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

    def test_validate_file_cached_ignore(self):
        """Test that validating a file with cached spec against the core namespace succeeds."""
        result = subprocess.run(["coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/1.1.2_nwbfile.nwb",
                                 "--no-cached-namespace"], capture_output=True)

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against PyNWB namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_invalid(self):
        """Test that validating an invalid file outputs errors."""
        result = subprocess.run(
            [
                "coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/1.0.2_str_experimenter.nwb",
                "--no-cached-namespace"
            ],
            capture_output=True
        )

        stderr_regex = re.compile(
            r" - found the following errors:\s*"
            r"root/general/experimenter \(general/experimenter\): incorrect shape - expected an array of shape "
            r"'\[None\]', got non-array data 'one experimenter'\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.0\.2_str_experimenter\.nwb against PyNWB namespace information using "
            r"namespace 'core'\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_list_namespaces_core(self):
        """Test listing namespaces from a file"""
        result = subprocess.run(
            [
                "coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/1.1.2_nwbfile.nwb",
                "--list-namespaces"
            ],
            capture_output=True
        )

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(r"core\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_list_namespaces_extension(self):
        """Test listing namespaces from a file with an extension"""
        result = subprocess.run(
            [
                "coverage", "run", "-p", "-m", "pynwb.validate", "tests/back_compat/2.1.0_nwbfile_with_extension.nwb",
                "--list-namespaces"
            ],
            capture_output=True
        )

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(r"ndx-testextension\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)


class TestValidateFunction(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specificaitions

    def test_validate_io_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        with NWBHDF5IO('tests/back_compat/1.0.2_nwbfile.nwb', 'r') as io:
            errors = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.0.2_nwbfile.nwb', 'r') as io:
            with self.assertRaisesWith(KeyError, "\"'notfound' not a namespace\""):
                validate(io, 'notfound')

    def test_validate_io_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            errors = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension(self):
        """Test that validating a file with cached spec against its cached namespaces succeeds."""
        with NWBHDF5IO('tests/back_compat/2.1.0_nwbfile_with_extension.nwb', 'r', load_namespaces=True) as io:
            errors = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension_pass_ns(self):
        """Test that validating a file with cached extension spec against the extension namespace succeeds."""
        with NWBHDF5IO('tests/back_compat/2.1.0_nwbfile_with_extension.nwb', 'r', load_namespaces=True) as io:
            errors = validate(io, 'ndx-testextension')
            self.assertEqual(errors, [])

    def test_validate_io_cached_core_with_io(self):
        """
        For back-compatability, test that validating a file with cached extension spec against the core
        namespace succeeds when using the `io` + `namespace` keywords.
        """
        with NWBHDF5IO(
            path='tests/back_compat/2.1.0_nwbfile_with_extension.nwb', mode='r', load_namespaces=True
        ) as io:
            results = validate(io=io, namespace="core")
            self.assertEqual(results, [])

    def test_validate_file_cached_extension(self):
        """
        Test that validating a file with cached extension spec against the core
        namespace raises an error with the new CLI-mimicing paths keyword.
        """
        nwbfile_path = "tests/back_compat/2.1.0_nwbfile_with_extension.nwb"
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                results, status = validate(paths=[nwbfile_path], namespace="core", verbose=True)
                self.assertEqual(results, [])
                self.assertEqual(status, 1)
                self.assertEqual(
                    fake_err.getvalue(),
                    (
                        "The namespace 'core' is included by the namespace 'ndx-testextension'. "
                        "Please validate against that namespace instead.\n"
                    )
                )
                self.assertEqual(fake_out.getvalue(), "")

    def test_validate_file_cached_core(self):
        """
        Test that validating a file with cached core spec with verbose=False.
        """
        nwbfile_path = "tests/back_compat/1.1.2_nwbfile.nwb"
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                results, status = validate(paths=[nwbfile_path], namespace="core")
                self.assertEqual(results, [])
                self.assertEqual(status, 0)
                self.assertEqual(fake_err.getvalue(), "")
                self.assertEqual(fake_out.getvalue(), "")

    def test_validate_file_cached_no_cache_bad_ns(self):
        """
        Test that validating a file with no cached namespace, a namespace that is not found, and verbose=False.
        """
        nwbfile_path = "tests/back_compat/1.0.2_nwbfile.nwb"
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                results, status = validate(paths=[nwbfile_path], namespace="notfound")
                self.assertEqual(results, [])
                self.assertEqual(status, 1)
                stderr_regex = (
                    r"The namespace 'notfound' could not be found in PyNWB namespace information as only "
                    r"\['core'\] is present.\n"
                )
                self.assertRegex(fake_err.getvalue(), stderr_regex)
                self.assertEqual(fake_out.getvalue(), "")

    def test_validate_io_cached_bad_ns(self):
        """Test that validating a file with cached spec against a specified, unknown namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            with self.assertRaisesWith(KeyError, "\"'notfound' not a namespace\""):
                validate(io, 'notfound')

    def test_validate_io_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        with NWBHDF5IO('tests/back_compat/1.1.2_nwbfile.nwb', 'r') as io:
            # TODO this error should not be different from the error when using the validate script above
            msg = "builder must have data type defined with attribute 'data_type'"
            with self.assertRaisesWith(ValueError, msg):
                validate(io, 'hdmf-common')
