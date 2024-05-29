import subprocess
import re
import sys
from unittest.mock import patch
from io import StringIO
import warnings

from pynwb.testing import TestCase
from pynwb import validate, NWBHDF5IO


# NOTE we use "coverage run -m pynwb.validate" instead of "python -m pynwb.validate"
# so that we can both test pynwb.validate and compute code coverage from that test.
# NOTE we also use "coverage run -p" which will generate a .coverage file with the
# machine name, process id, and a random number appended to the filename to
# simplify collecting and merging coverage data from multiple subprocesses. if "-p"
# is not used, then each "coverage run" will overwrite the .coverage file from a
# previous "coverage run".
# NOTE we run "coverage" as "{sys.executable} -m coverage" to 1. make sure to use
# the same python version, and on Debian systems executable is "python3-coverage", not
# just "coverage".
# NOTE the run_coverage.yml GitHub Action runs "python -m coverage combine" to
# combine the individual coverage reports into one .coverage file.
def run_coverage(extra_args: list[str]):
    return subprocess.run(
        [sys.executable, "-m", "coverage", "run", "-p", "-m", "pynwb.validate"]
        + extra_args,
        capture_output=True
    )


class TestValidateCLI(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specifications

    def test_validate_file_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        result = run_coverage(["tests/back_compat/1.0.2_nwbfile.nwb"])

        stderr_regex = re.compile(
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
        result = run_coverage(["tests/back_compat/1.0.2_nwbfile.nwb", "--ns", "notfound"])

        stderr_regex = re.compile(
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to PyNWB namespace information\.\s*"
            r"The namespace 'notfound' could not be found in PyNWB namespace information as only "
            r"\['core'\] is present\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        result = run_coverage(["tests/back_compat/1.1.2_nwbfile.nwb"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against cached namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_bad_ns(self):
        """Test that validating a file with cached spec against a specified, unknown namespace fails."""
        result = run_coverage(["tests/back_compat/1.1.2_nwbfile.nwb", "--ns", "notfound"])

        stderr_regex = re.compile(
            r"The namespace 'notfound' could not be found in cached namespace information as only "
            r"\['core'\] is present\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

        self.assertEqual(result.stdout.decode('utf-8'), '')

    def test_validate_file_cached_extension(self):
        """Test that validating a file with cached spec against the cached namespaces succeeds."""
        result = run_coverage(["tests/back_compat/2.1.0_nwbfile_with_extension.nwb"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/2\.1\.0_nwbfile_with_extension\.nwb against cached namespace information "
            r"using namespace 'ndx-testextension'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_extension_pass_ns(self):
        """Test that validating a file with cached spec against the extension namespace succeeds."""
        result = run_coverage(["tests/back_compat/2.1.0_nwbfile_with_extension.nwb", "--ns", "ndx-testextension"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/2\.1\.0_nwbfile_with_extension\.nwb against cached namespace information "
            r"using namespace 'ndx-testextension'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_core(self):
        """Test that validating a file with cached spec against the core namespace succeeds."""
        result = run_coverage(["tests/back_compat/2.1.0_nwbfile_with_extension.nwb", "--ns", "core"])

        stdout_regex = re.compile(
            r"The namespace 'core' is included by the namespace 'ndx-testextension'. "
            r"Please validate against that namespace instead\.\s*"
        )
        self.assertRegex(result.stderr.decode('utf-8'), stdout_regex)

    def test_validate_file_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        result = run_coverage(["tests/back_compat/1.1.2_nwbfile.nwb", "--ns", "hdmf-common"])

        stderr_regex = re.compile(
            r"The namespace 'hdmf-common' is included by the namespace 'core'\. Please validate against that "
            r"namespace instead\.\s*",
        )
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex)

    def test_validate_file_cached_ignore(self):
        """Test that validating a file with cached spec against the core namespace succeeds."""
        result = run_coverage(["tests/back_compat/1.1.2_nwbfile.nwb", "--no-cached-namespace"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(
            r"Validating tests/back_compat/1\.1\.2_nwbfile\.nwb against PyNWB namespace information using namespace "
            r"'core'\.\s* - no errors found\.\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_invalid(self):
        """Test that validating an invalid file outputs errors."""
        result = run_coverage(["tests/back_compat/1.0.2_str_experimenter.nwb", "--no-cached-namespace"])

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
        result = run_coverage(["tests/back_compat/1.1.2_nwbfile.nwb", "--list-namespaces"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(r"core\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)

    def test_validate_file_list_namespaces_extension(self):
        """Test listing namespaces from a file with an extension"""
        result = run_coverage(["tests/back_compat/2.1.0_nwbfile_with_extension.nwb", "--list-namespaces"])

        self.assertEqual(result.stderr.decode('utf-8'), '')

        stdout_regex = re.compile(r"ndx-testextension\s*")
        self.assertRegex(result.stdout.decode('utf-8'), stdout_regex)


class TestValidateFunction(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specificaitions

    def get_io(self, path):
        """Get an NWBHDF5IO object for the given path, ignoring the warning about ignoring cached namespaces."""
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Ignoring cached namespace .*",
                category=UserWarning,
            )
            return NWBHDF5IO(str(path), 'r')

    def test_validate_io_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        with self.get_io('tests/back_compat/1.0.2_nwbfile.nwb') as io:
            errors, _ = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io('tests/back_compat/1.0.2_nwbfile.nwb') as io:
                    results, status = validate(io=io, namespace='notfound')
                    self.assertEqual(results, [])
                    self.assertEqual(status, 1)
                    stderr_regex = (
                        r"The namespace 'notfound' could not be found in PyNWB namespace information as only "
                        r"\['core'\] is present.\n"
                    )
                self.assertRegex(fake_err.getvalue(), stderr_regex)
                self.assertEqual(fake_out.getvalue(), "")

    def test_validate_io_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        with self.get_io('tests/back_compat/1.1.2_nwbfile.nwb') as io:
            errors, _ = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension(self):
        """Test that validating a file with cached spec against its cached namespaces succeeds."""
        with self.get_io('tests/back_compat/2.1.0_nwbfile_with_extension.nwb') as io:
            errors, _ = validate(io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension_pass_ns(self):
        """Test that validating a file with cached extension spec against the extension namespace succeeds."""
        with self.get_io('tests/back_compat/2.1.0_nwbfile_with_extension.nwb') as io:
            errors, _ = validate(io, 'ndx-testextension')
            self.assertEqual(errors, [])

    def test_validate_io_cached_core_with_io(self):
        """
        Test that validating a file with cached extension spec against the core
        namespace succeeds rases an error when using the `io` + `namespace` keywords.
        """
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io(path='tests/back_compat/2.1.0_nwbfile_with_extension.nwb') as io:
                    results, status = validate(io=io, namespace="core", verbose=True)
                    self.assertEqual(results, [])
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        fake_err.getvalue(),
                        (
                            "The namespace 'core' is included by the namespace 'ndx-testextension'. "
                            "Please validate against that namespace instead.\n"
                        )
                    )
                    self.assertEqual(fake_out.getvalue(),"")

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
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io('tests/back_compat/1.1.2_nwbfile.nwb') as io:
                    results, status = validate(io=io, namespace='notfound')
                    self.assertEqual(results, [])
                    self.assertEqual(status, 1)
                    stderr_regex = (
                        r"The namespace 'notfound' could not be found in cached namespace information as only "
                        r"\['core'\] is present.\n"
                    )
                self.assertRegex(fake_err.getvalue(), stderr_regex)
                self.assertEqual(fake_out.getvalue(), "")

    def test_validate_io_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io(path='tests/back_compat/1.1.2_nwbfile.nwb') as io:
                    results, status = validate(io=io, namespace="hdmf-common", verbose=True)
                    self.assertEqual(results, [])
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        fake_err.getvalue(),
                        (
                            "The namespace 'hdmf-common' is included by the namespace 'core'. "
                            "Please validate against that namespace instead.\n"
                        )
                    )
                    self.assertEqual(fake_out.getvalue(), "")

    def test_validate_io_and_path_same(self):
        """Test that validating a file with an io object and a path return the same results."""
        path = 'tests/back_compat/1.1.2_nwbfile.nwb'
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io(path=path) as io:
                    results_io, status_io = validate(io=io, namespace="hdmf-common", verbose=True)
                    fake_err_io = fake_err.getvalue()
                    fake_out_io = fake_out.getvalue()

        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                results_path, status_path = validate(paths=[path], namespace="hdmf-common", verbose=True)
                fake_err_path = fake_err.getvalue()
                fake_out_path = fake_out.getvalue()

        self.assertEqual(results_io, results_path)
        self.assertEqual(status_io, status_path)
        self.assertEqual(fake_err_io, fake_err_path)
        self.assertEqual(fake_out_io, fake_out_path)
