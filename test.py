#!/usr/bin/env python

import argparse
import inspect
import logging
import os.path
import sys
import traceback
import unittest2 as unittest

flags = {'form': 1, 'pynwb': 2, 'integration': 3, 'example': 4}

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

    runner = unittest.TextTestRunner(verbosity=verbose, resultclass=SuccessRecordingResult)
    pynwb_test_result = runner.run(unittest.TestLoader().discover(directory))

    TOTAL += pynwb_test_result.testsRun
    FAILURES += len(pynwb_test_result.failures)
    ERRORS += len(pynwb_test_result.errors)

    return pynwb_test_result


def _import_from_file(script):
    import imp
    return imp.load_source(os.path.basename(script), script)


def run_example_tests():
    global TOTAL, FAILURES, ERRORS
    logging.info('running example tests')
    examples_dir = os.path.join(os.path.dirname(__file__), "docs", "code")
    examples_scripts = [
        os.path.join(examples_dir, script) for script in os.listdir(examples_dir) if script.endswith(".py")]
    examples_dir = os.path.join(os.path.dirname(__file__), "docs", "gallery", "examples")
    examples_scripts += [
        os.path.join(examples_dir, script) for script in os.listdir(examples_dir) if script.endswith(".py")]
    TOTAL += len(examples_scripts)
    for script in examples_scripts:
        try:
            logging.info("Executing %s" % script)
            example = _import_from_file(script)
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
    required_tests = {}
    for test_case in test_cases:
        if not hasattr(test_case, 'container'):
            continue
        container_class = test_case.container.__class__

        if container_class not in tested_containers:
            tested_containers[container_class] = [test_case._testMethodName]
        else:
            tested_containers[container_class].append(test_case._testMethodName)

        if container_class not in required_tests:
            required_tests[container_class] = list(test_case.required_tests)
        else:
            required_tests[container_class].extend(test_case.required_tests)

    count_missing = 0
    for container_class in type_map.get_container_classes('core'):

        if container_class not in tested_containers:
            count_missing += 1
            if verbose > 1:
                logging.info('%s missing test case; should define in %s' % (container_class,
                                                                            inspect.getfile(container_class)))
            continue

        test_methods = tested_containers[container_class]
        required = required_tests[container_class]
        methods_missing = set(required) - set(test_methods)

        if methods_missing != set([]):
            count_missing += 1
            if verbose > 1:
                logging.info('%s missing test method(s) \"%s\"; should define in %s' % (
                    container_class, ', '.join(methods_missing), inspect.getfile(container_class)))

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
    parser.add_argument('-f', '--form', action='append_const', const=flags['form'], dest='suites',
                        help='run unit tests for form package')
    parser.add_argument('-p', '--pynwb', action='append_const', const=flags['pynwb'], dest='suites',
                        help='run unit tests for pynwb package')
    parser.add_argument('-i', '--integration', action='append_const', const=flags['integration'], dest='suites',
                        help='run integration tests')
    parser.add_argument('-e', '--example', action='append_const', const=flags['example'], dest='suites',
                        help='run example tests')
    args = parser.parse_args()
    if not args.suites:
        args.suites = list(flags.values())

    # set up logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('======================================================================\n'
                                  '%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Run unit tests for form package
    if flags['form'] in args.suites:
        run_test_suite("tests/unit/form_tests", "form unit tests", verbose=args.verbosity)

    # Run unit tests for pynwb package
    if flags['pynwb'] in args.suites:
        run_test_suite("tests/unit/pynwb_tests", "pynwb unit tests", verbose=args.verbosity)

    # Run example tests
    if flags['example'] in args.suites:
        run_example_tests()

    # Run integration tests
    if flags['integration'] in args.suites:
        run_integration_tests(verbose=args.verbosity)

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
