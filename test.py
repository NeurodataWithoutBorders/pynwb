#!/usr/bin/env python
import warnings
import re
import argparse
import glob
import inspect
import logging
import os.path
import os
import sys
import traceback
import unittest
from tests.coloredtestrunner import ColoredTestRunner, ColoredTestResult

flags = {'pynwb': 2, 'integration': 3, 'example': 4, 'backwards': 5}

TOTAL = 0
FAILURES = 0
ERRORS = 0


def run_test_suite(directory, description="", verbose=True):
    global TOTAL, FAILURES, ERRORS
    logging.info("running %s" % description)
    directory = os.path.join(os.path.dirname(__file__), directory)
    if verbose > 1:
        runner = ColoredTestRunner(verbosity=verbose)
    else:
        runner = unittest.TextTestRunner(verbosity=verbose, resultclass=ColoredTestResult)
    test_result = runner.run(unittest.TestLoader().discover(directory))

    TOTAL += test_result.testsRun
    FAILURES += len(test_result.failures)
    ERRORS += len(test_result.errors)

    return test_result


def _import_from_file(script):
    import imp
    return imp.load_source(os.path.basename(script), script)


warning_re = re.compile("Parent module '[a-zA-Z0-9]+' not found while handling absolute import")


def run_example_tests():
    global TOTAL, FAILURES, ERRORS
    logging.info('running example tests')
    examples_scripts = list()
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "docs", "gallery")):
        for f in files:
            if f.endswith(".py"):
                examples_scripts.append(os.path.join(root, f))

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
        except Exception:
            print(traceback.format_exc())
            FAILURES += 1
            ERRORS += 1


def validate_nwbs():
    global TOTAL, FAILURES, ERRORS
    logging.info('running validation tests on NWB files')
    examples_nwbs = glob.glob('*.nwb')

    import pynwb

    TOTAL += len(examples_nwbs)
    for nwb in examples_nwbs:
        try:
            logging.info("Validating file %s" % nwb)

            ws = list()
            with warnings.catch_warnings(record=True) as tmp:
                with pynwb.NWBHDF5IO(nwb, mode='r') as io:
                    errors = pynwb.validate(io)
                    if errors:
                        FAILURES += 1
                        ERRORS += 1
                        for err in errors:
                            print("Error: %s" % err)
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
    pynwb_test_result = run_test_suite("tests/integration", "integration tests", verbose=verbose)
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
    parser.add_argument('-b', '--backwards', action='append_const', const=flags['backwards'], dest='suites',
                        help='run backwards compatibility tests')
    args = parser.parse_args()
    if not args.suites:
        args.suites = list(flags.values())
        args.suites.pop(args.suites.index(flags['example']))  # remove example as a suite run by default

    # set up logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
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
    if flags['example'] in args.suites:
        run_example_tests()
        validate_nwbs()

    # Run integration tests
    if flags['integration'] in args.suites:
        run_integration_tests(verbose=args.verbosity)

    if flags['backwards'] in args.suites:
        run_test_suite("tests/back_compat", "pynwb backwards compatibility tests", verbose=args.verbosity)

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
