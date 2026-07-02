import subprocess
import re
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from pynwb.testing import TestCase
from pynwb.testing.mock.file import mock_NWBFile
from pynwb import validate, NWBHDF5IO

try:
    from hdmf_zarr import NWBZarrIO  # noqa: F401
    HAVE_NWBZarrIO = True
except ImportError:
    HAVE_NWBZarrIO = False


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
        [sys.executable, "-m", "coverage", "run", "-p", "-m", "pynwb.validation_cli"]
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

        stderr_regex_1 = re.compile(
            r"The file tests/back_compat/1\.0\.2_nwbfile\.nwb has no cached namespace information\. "
            r"Falling back to PyNWB namespace information\.\s*")
        stderr_regex_2 = re.compile(
            r"The namespace 'notfound' could not be found in PyNWB namespace information as only "
            r"\['core'\] is present\.\s*")
        
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex_1)
        self.assertRegex(result.stderr.decode('utf-8'), stderr_regex_2)

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

    def test_validate_file_json_output(self):
        """Test that validating a file with the json flag outputs a json file."""
        json_path = "test_validation.json"
        run_coverage(["tests/back_compat/1.0.2_str_experimenter.nwb", "--no-cached-namespace", 
                      "--json-output-path", json_path])
        self.assertTrue(os.path.exists(json_path))
        os.remove(json_path)

    def test_validation_entry_point(self):
        """Test that using the validation entry point successfully executes the validate CLI."""
        json_path = "test_validation_entry_point.json"
        subprocess.run(["pynwb-validate", "tests/back_compat/1.0.2_str_experimenter.nwb", 
                        "--json-output-path", json_path])
        self.assertTrue(os.path.exists(json_path))
        os.remove(json_path)


class TestValidateFunction(TestCase):

    # 1.0.2_nwbfile.nwb has no cached specifications
    # 1.0.3_nwbfile.nwb has cached "core" specification
    # 1.1.2_nwbfile.nwb has cached "core" and "hdmf-common" specificaitions

    def get_io(self, path):
        """Get an NWBHDF5IO object for the given path, ignoring the warning about ignoring cached namespaces."""
        return NWBHDF5IO(str(path), 'r')

    def test_validate_io_no_cache(self):
        """Test that validating a file with no cached spec against the core namespace succeeds."""
        with self.get_io('tests/back_compat/1.0.2_nwbfile.nwb') as io:
            errors = validate(io=io)
            self.assertEqual(errors, [])

    def test_validate_io_no_cache_bad_ns(self):
        """Test that validating a file with no cached spec against a specified, unknown namespace fails."""
        expected_error = ("The namespace 'notfound' could not be found in PyNWB namespace information as only "
                          "['core'] is present.")
        with self.assertRaisesWith(ValueError, expected_error):
            with self.get_io('tests/back_compat/1.0.2_nwbfile.nwb') as io:
                validate(io=io, namespace='notfound')

    def test_validate_io_cached(self):
        """Test that validating a file with cached spec against its cached namespace succeeds."""
        with self.get_io('tests/back_compat/1.1.2_nwbfile.nwb') as io:
            errors = validate(io=io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension(self):
        """Test that validating a file with cached spec against its cached namespaces succeeds."""
        with self.get_io('tests/back_compat/2.1.0_nwbfile_with_extension.nwb') as io:
            errors = validate(io=io)
            self.assertEqual(errors, [])

    def test_validate_io_cached_extension_pass_ns(self):
        """Test that validating a file with cached extension spec against the extension namespace succeeds."""
        with self.get_io('tests/back_compat/2.1.0_nwbfile_with_extension.nwb') as io:
            errors = validate(io=io, namespace='ndx-testextension')
            self.assertEqual(errors, [])

    def test_validate_file_cached_extension(self):
        """
        Test that validating a file with cached extension spec against the core
        namespace raises an error with the new CLI-mimicing paths keyword.
        """
        nwbfile_path = "tests/back_compat/2.1.0_nwbfile_with_extension.nwb"
        expected_error = ("The namespace 'core' is included by the namespace 'ndx-testextension'. "
                          "Please validate against that namespace instead.")
        with self.assertRaisesWith(ValueError, expected_error):
            validate(path=nwbfile_path, namespace="core", verbose=True)

    def test_validate_file_cached_core(self):
        """
        Test that validating a file with cached core spec with verbose=False.
        """
        nwbfile_path = "tests/back_compat/1.1.2_nwbfile.nwb"
        results = validate(path=nwbfile_path, namespace="core")
        self.assertEqual(results, [])

    def test_validate_file_cached_no_cache_bad_ns(self):
        """
        Test that validating a file with no cached namespace, a namespace that is not found, and verbose=False.
        """
        nwbfile_path = "tests/back_compat/1.0.2_nwbfile.nwb"
        expected_error = ("The namespace 'notfound' could not be found in PyNWB namespace information as only "
                          "['core'] is present.")
        with self.assertRaisesWith(ValueError, expected_error):
            validate(path=nwbfile_path, namespace="notfound")

    def test_validate_io_cached_hdmf_common(self):
        """Test that validating a file with cached spec against the hdmf-common namespace fails."""
        expected_error = ("The namespace 'hdmf-common' is included by the namespace 'core'. "
                          "Please validate against that namespace instead.")
        with self.assertRaisesWith(ValueError, expected_error):
            with self.get_io(path='tests/back_compat/1.1.2_nwbfile.nwb') as io:
                validate(io=io, namespace="hdmf-common", verbose=True)

    def test_validate_io_and_path_same(self):
        """Test that validating a file with an io object and a path return the same results."""
        tests = [('tests/back_compat/1.1.2_nwbfile.nwb', None),
                 ('tests/back_compat/1.1.2_nwbfile.nwb', 'core'),
                 ('tests/back_compat/2.1.0_nwbfile_with_extension.nwb', None),
                 ('tests/back_compat/2.1.0_nwbfile_with_extension.nwb', 'ndx-testextension'),]
        
        tests_with_error = [('tests/back_compat/1.1.2_nwbfile.nwb', 'notfound'),
                            ('tests/back_compat/1.1.2_nwbfile.nwb', 'hdmf-common'),
                            ('tests/back_compat/2.1.0_nwbfile_with_extension.nwb', 'core'),]
        
        tests_with_warning = [('tests/back_compat/1.0.2_nwbfile.nwb', None),]

        # paths that cause no errors
        for path, ns in tests:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with self.get_io(path=path) as io:
                    results_io = validate(io=io, namespace=ns, verbose=True)
                out_io = fake_out.getvalue()        

            with patch("sys.stdout", new=StringIO()) as fake_out:
                results_path = validate(path=path, namespace=ns, verbose=True)
                out_path = fake_out.getvalue()

            # remove path from error messages since it will not be included in io outputs
            out_path = out_path.replace(f'{path} ', '')
            self.assertEqual(results_io, results_path)
            self.assertEqual(out_io, out_path)

        #paths that return warnings
        for path, ns in tests_with_warning:
            with self.assertWarns(UserWarning) as w_io:
                with self.get_io(path=path) as io:
                    results_io = validate(io=io, namespace=ns, verbose=True)

            with self.assertWarns(UserWarning) as w_path:
                results_path = validate(path=path, namespace=ns, verbose=True)

            # remove path from error messages since it will not be included in io outputs
            out_path = str(w_path.warning).replace(f'{path} ', '')
            self.assertEqual(str(w_io.warning), out_path)

        # paths that return errors
        for path, ns in tests_with_error:
            with self.assertRaises(ValueError) as e_io:
                with self.get_io(path=path) as io:
                    results_io = validate(io=io, namespace=ns, verbose=True)
            
            with self.assertRaises(ValueError) as e_path:
                results_path = validate(path=path, namespace=ns, verbose=True)

            # remove path from error messages since it will not be included in io outputs
            self.assertEqual(str(e_io.exception), str(e_path.exception))


@unittest.skipIf(not HAVE_NWBZarrIO, "hdmf-zarr is not installed")
class TestValidateZarr(TestCase):
    # Regression tests for https://github.com/NeurodataWithoutBorders/pynwb/issues/2131:
    # validate(path=...) on a Zarr-backed NWB file used to raise TypeError because
    # HDF5-only kwargs leaked into NWBZarrIO. The validator now opens via a
    # backend-aware factory and uses load_namespaces_io on the open IO.

    def _write_zarr_nwbfile(self, path):
        nwbfile = mock_NWBFile()
        with NWBZarrIO(str(path), 'w') as io:
            io.write(nwbfile)

    def test_validate_zarr_path_cached_namespaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.nwb.zarr"
            self._write_zarr_nwbfile(path)
            errors = validate(path=str(path))
            self.assertEqual(errors, [])

    def test_validate_zarr_path_no_cached_namespaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.nwb.zarr"
            self._write_zarr_nwbfile(path)
            errors = validate(path=str(path), use_cached_namespaces=False)
            self.assertEqual(errors, [])

    def test_validate_zarr_io(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.nwb.zarr"
            self._write_zarr_nwbfile(path)
            with NWBZarrIO(str(path), 'r') as io:
                errors = validate(io=io)
            self.assertEqual(errors, [])
