#!/usr/bin/env python
import warnings
import re
import argparse
import glob
import inspect
import logging
import os.path
import os
import shutil
from subprocess import run, PIPE, STDOUT
import sys
import traceback
import unittest
import importlib.util

flags = {
    'pynwb': 2,
    'integration': 3,
    'example': 4,
    'backwards': 5,
    'validate-examples': 6,
    'ros3': 7,
    'example-ros3': 8,
    'validation-module': 9
}

TOTAL = 0
FAILURES = 0
ERRORS = 0


class SuccessRecordingResult(unittest.TextTestResult):
    '''A unittest test result class that stores successful test cases as well
    as failures and skips.
    '''

    def addSuccess(self, test):
        if not hasattr(self, 'successes'):
            self.successes = [test]
        else:
            self.successes.append(test)

    def get_all_cases_run(self):
        '''Return a list of each test case which failed or succeeded
        '''
        cases = []

        if hasattr(self, 'successes'):
            cases.extend(self.successes)
        cases.extend([failure[0] for failure in self.failures])

        return cases


def run_test_suite(directory, description="", verbose=True):
    global TOTAL, FAILURES, ERRORS
    logging.info("running %s" % description)
    directory = os.path.join(os.path.dirname(__file__), directory)
    runner = unittest.TextTestRunner(verbosity=verbose, resultclass=SuccessRecordingResult)
    # set top_level_dir below to prevent import name clashes between
    # tests/unit/test_base.py and tests/integration/hdf5/test_base.py
    test_result = runner.run(unittest.TestLoader().discover(directory, top_level_dir='tests'))

    TOTAL += test_result.testsRun
    FAILURES += len(test_result.failures)
    ERRORS += len(test_result.errors)

    return test_result


def _import_from_file(script):
    modname = os.path.basename(script)
    spec = importlib.util.spec_from_file_location(os.path.basename(script), script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)


warning_re = re.compile("Parent module '[a-zA-Z0-9]+' not found while handling absolute import")


ros3_examples = [
    os.path.join('general', 'read_basics.py'),
    os.path.join('advanced_io', 'streaming.py'),
]

allensdk_examples = [
    os.path.join('domain', 'brain_observatory.py'),  # TODO create separate workflow for this
]


def run_example_tests():
    """Run the Sphinx gallery example files, excluding ROS3-dependent ones, to check for errors."""
    logging.info('running example tests')
    examples_scripts = list()
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "docs", "gallery")):
        for f in files:
            if f.endswith(".py"):
                name_with_parent_dir = os.path.join(os.path.basename(root), f)
                if name_with_parent_dir in ros3_examples or name_with_parent_dir in allensdk_examples:
                    logging.info("Skipping %s" % name_with_parent_dir)
                    continue
                examples_scripts.append(os.path.join(root, f))

    __run_example_tests_helper(examples_scripts)


def run_example_ros3_tests():
    """Run the Sphinx gallery example files that depend on ROS3 to check for errors."""
    logging.info('running example ros3 tests')
    examples_scripts = list()
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "docs", "gallery")):
        for f in files:
            if f.endswith(".py"):
                name_with_parent_dir = os.path.join(os.path.basename(root), f)
                if name_with_parent_dir not in ros3_examples:
                    logging.info("Skipping %s" % name_with_parent_dir)
                    continue
                examples_scripts.append(os.path.join(root, f))

    __run_example_tests_helper(examples_scripts)


def __run_example_tests_helper(examples_scripts):
    global TOTAL, FAILURES, ERRORS
    TOTAL += len(examples_scripts)
    for script in examples_scripts:
        try:
            logging.info("Executing %s" % script)
            ws = list()
            with warnings.catch_warnings(record=True) as tmp:
                _import_from_file(script)
                for w in tmp:  # ignore RunTimeWarnings about importing
                    if isinstance(w.message, RuntimeWarning) and not warning_re.match(str(w.message)):
                        ws.append(w)
            for w in ws:
                warnings.showwarning(w.message, w.category, w.filename, w.lineno, w.line)
        except (ImportError, ValueError, ModuleNotFoundError) as e:
            if "linkml" in str(e):
                pass  # this is OK because linkml is not always installed
            else:
                raise e
        except Exception:
            print(traceback.format_exc())
            FAILURES += 1
            ERRORS += 1


def validate_nwbs():
    global TOTAL, FAILURES, ERRORS
    logging.info('running validation tests on NWB files')
    examples_nwbs = glob.glob('*.nwb')

    import pynwb

    for nwb in examples_nwbs:
        try:
            logging.info("Validating file %s" % nwb)

            ws = list()
            with warnings.catch_warnings(record=True) as tmp:
                logging.info("Validating with pynwb.validate method.")
                with pynwb.NWBHDF5IO(nwb, mode='r') as io:
                    errors = pynwb.validate(io)
                    TOTAL += 1

                    if errors:
                        FAILURES += 1
                        ERRORS += 1
                        for err in errors:
                            print("Error: %s" % err)

                def get_namespaces(nwbfile):
                    comp = run(["python", "-m", "pynwb.validate",
                               "--list-namespaces", nwbfile],
                               stdout=PIPE, stderr=STDOUT, universal_newlines=True, timeout=30)

                    if comp.returncode != 0:
                        return []

                    return comp.stdout.split()

                namespaces = get_namespaces(nwb)

                if len(namespaces) == 0:
                    FAILURES += 1
                    ERRORS += 1

                cmds = []
                cmds += [["python", "-m", "pynwb.validate", nwb]]
                cmds += [["python", "-m", "pynwb.validate", "--no-cached-namespace", nwb]]

                for ns in namespaces:
                    # for some reason, this logging command is necessary to correctly printing the namespace in the
                    # next logging command
                    logging.info("Namespace found: %s" % ns)
                    cmds += [["python", "-m", "pynwb.validate", "--ns", ns, nwb]]

                for cmd in cmds:
                    logging.info("Validating with \"%s\"." % (" ".join(cmd[:-1])))
                    comp = run(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True, timeout=30)
                    TOTAL += 1

                    if comp.returncode != 0:
                        FAILURES += 1
                        ERRORS += 1
                        print("Error: %s" % comp.stdout)

                for w in tmp:  # ignore RunTimeWarnings about importing
                    if isinstance(w.message, RuntimeWarning) and not warning_re.match(str(w.message)):
                        ws.append(w)
            for w in ws:
                warnings.showwarning(w.message, w.category, w.filename, w.lineno, w.line)
        except Exception:
            print(traceback.format_exc())
            FAILURES += 1
            ERRORS += 1


def run_integration_tests(verbose=True):
    pynwb_test_result = run_test_suite("tests/integration/hdf5", "integration tests", verbose=verbose)
    test_cases = pynwb_test_result.get_all_cases_run()

    import pynwb
    type_map = pynwb.get_type_map()

    tested_containers = {}
    for test_case in test_cases:
        if not hasattr(test_case, 'container'):
            continue
        container_class = test_case.container.__class__

        if container_class not in tested_containers:
            tested_containers[container_class] = [test_case._testMethodName]
        else:
            tested_containers[container_class].append(test_case._testMethodName)

    count_missing = 0
    for container_class in type_map.get_container_classes('core'):
        if container_class not in tested_containers:
            count_missing += 1
            if verbose > 1:
                logging.info('%s missing test case; should define in %s' % (container_class,
                                                                            inspect.getfile(container_class)))

    if count_missing > 0:
        logging.info('%d classes missing integration tests in ui_write' % count_missing)
    else:
        logging.info('all classes have integration tests')

    run_test_suite("tests/integration/utils", "integration utils tests", verbose=verbose)


def clean_up_tests():
    # remove files generated from running example files
    files_to_remove = [
        "advanced_io_example.nwb",
        "basic_alternative_custom_write.nwb",
        "basic_iterwrite_example.nwb",
        "basic_sparse_iterwrite_*.nwb",
        "basic_sparse_iterwrite_*.npy",
        "basics_tutorial.nwb",
        "behavioral_tutorial.nwb",
        "brain_observatory.nwb",
        "cache_spec_example.nwb",
        "ecephys_tutorial.nwb",
        "ecog.extensions.yaml",
        "ecog.namespace.yaml",
        "ex_test_icephys_file.nwb",
        "example_timeintervals_file.nwb",
        "exported_nwbfile.nwb",
        "external_linkcontainer_example.nwb",
        "external_linkdataset_example.nwb",
        "external1_example.nwb",
        "external2_example.nwb",
        "icephys_example.nwb",
        "icephys_pandas_testfile.nwb",
        "images_tutorial.nwb",
        "manifest.json",
        "mylab.extensions.yaml",
        "mylab.namespace.yaml",
        "nwbfile.nwb",
        "ophys_tutorial.nwb",
        "processed_data.nwb",
        "raw_data.nwb",
        "scratch_analysis.nwb",
        "sub-P11HMH_ses-20061101_ecephys+image.nwb",
        "test_edit.nwb",
        "test_edit2.nwb",
        "test_cortical_surface.nwb",
        "test_icephys_file.nwb",
        "test_multicontainerinterface.extensions.yaml",
        "test_multicontainerinterface.namespace.yaml",
        "test_multicontainerinterface.nwb",
    ]
    for f in files_to_remove:
        for name in glob.glob(f):
            if os.path.exists(name):
                os.remove(name)

    shutil.rmtree("zarr_tutorial.nwb.zarr")


def main():
    # setup and parse arguments
    parser = argparse.ArgumentParser('python test.py [options]')
    parser.set_defaults(verbosity=1, suites=[])
    parser.add_argument('-v', '--verbose', const=2, dest='verbosity', action='store_const', help='run in verbose mode')
    parser.add_argument('-q', '--quiet', const=0, dest='verbosity', action='store_const', help='run disabling output')
    parser.add_argument('-p', '--pynwb', action='append_const', const=flags['pynwb'], dest='suites',
                        help='run unit tests for pynwb package')
    parser.add_argument('-i', '--integration', action='append_const', const=flags['integration'], dest='suites',
                        help='run integration tests')
    parser.add_argument('-e', '--example', action='append_const', const=flags['example'], dest='suites',
                        help='run example tests')
    parser.add_argument('-f', '--example-ros3', action='append_const', const=flags['example-ros3'], dest='suites',
                        help='run example tests with ros3 streaming')
    parser.add_argument('-b', '--backwards', action='append_const', const=flags['backwards'], dest='suites',
                        help='run backwards compatibility tests')
    parser.add_argument('-w', '--validate-examples', action='append_const', const=flags['validate-examples'],
                        dest='suites', help='run example tests and validation tests on example NWB files')
    parser.add_argument('-r', '--ros3', action='append_const', const=flags['ros3'], dest='suites',
                        help='run ros3 streaming tests')
    parser.add_argument('-x', '--validation-module', action='append_const', const=flags['validation-module'],
                        dest='suites', help='run tests on pynwb.validate')
    args = parser.parse_args()
    if not args.suites:
        args.suites = list(flags.values())
        # remove from test suites run by default
        args.suites.pop(args.suites.index(flags['example']))
        args.suites.pop(args.suites.index(flags['example-ros3']))
        args.suites.pop(args.suites.index(flags['validate-examples']))
        args.suites.pop(args.suites.index(flags['ros3']))
        args.suites.pop(args.suites.index(flags['validation-module']))

    # set up logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('======================================================================\n'
                                  '%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    warnings.simplefilter('always')

    warnings.filterwarnings("ignore", category=ImportWarning, module='importlib._bootstrap',
                            message=("can't resolve package from __spec__ or __package__, falling back on __name__ "
                                     "and __path__"))

    # Run unit tests for pynwb package
    if flags['pynwb'] in args.suites:
        run_test_suite("tests/unit", "pynwb unit tests", verbose=args.verbosity)

    # Run example tests
    is_run_example_tests = False
    if flags['example'] in args.suites or flags['validate-examples'] in args.suites:
        run_example_tests()
        is_run_example_tests = True

    # Run example tests with ros3 streaming examples
    # NOTE this requires h5py to be built with ROS3 support and the dandi package to be installed
    # this is most easily done by creating a conda environment using environment-ros3.yml
    if flags['example-ros3'] in args.suites:
        run_example_ros3_tests()

    # Run validation tests on the example NWB files generated above
    if flags['validate-examples'] in args.suites:
        validate_nwbs()

    # Run integration tests
    if flags['integration'] in args.suites:
        run_integration_tests(verbose=args.verbosity)

    # Run validation module tests, requires coverage to be installed
    if flags['validation-module'] in args.suites:
        run_test_suite("tests/validation", "validation tests", verbose=args.verbosity)

    # Run backwards compatibility tests
    if flags['backwards'] in args.suites:
        run_test_suite("tests/back_compat", "pynwb backwards compatibility tests", verbose=args.verbosity)

    # Run ros3 streaming tests
    if flags['ros3'] in args.suites:
        run_test_suite("tests/integration/ros3", "pynwb ros3 streaming tests", verbose=args.verbosity)

    # Delete files generated from running example tests above
    if is_run_example_tests:
        clean_up_tests()

    final_message = 'Ran %s tests' % TOTAL
    exitcode = 0
    if ERRORS > 0 or FAILURES > 0:
        exitcode = 1
        _list = list()
        if ERRORS > 0:
            _list.append('errors=%d' % ERRORS)
        if FAILURES > 0:
            _list.append('failures=%d' % FAILURES)
        final_message = '%s - FAILED (%s)' % (final_message, ','.join(_list))
    else:
        final_message = '%s - OK' % final_message

    logging.info(final_message)

    return exitcode


if __name__ == "__main__":
    sys.exit(main())
