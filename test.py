#!/usr/bin/env python

import argparse
import inspect
import logging
import sys
import unittest2 as unittest

import pynwb

flags = {'form': 1, 'pynwb': 2, 'integration': 3}

TOTAL = 0
FAILURES = 0
ERRORS = 0


def run_test_suite(directory, description="", verbose=True):
    global TOTAL, FAILURES, ERRORS
    logging.info("running %s" % description)
    pynwb_test_result = unittest.TextTestRunner(verbosity=verbose).run(
        unittest.TestLoader().discover(directory))
    TOTAL += pynwb_test_result.testsRun
    FAILURES += len(pynwb_test_result.failures)
    ERRORS += len(pynwb_test_result.errors)


def run_integration_tests(verbose=True):
    run_test_suite("tests/integration", "integration tests", verbose=verbose)

    type_map = pynwb.get_type_map()
    import imp
    name = 'integration'
    imp_result = imp.find_module(name, ['tests'])
    mod = imp.load_module(name, imp_result[0], imp_result[1], imp_result[2])

    d = mod.ui_write.base.container_tests
    MISSING_INT = list()
    for cls in type_map.get_container_classes('core'):
        if cls not in d:
            MISSING_INT.append(cls)

    if len(MISSING_INT) > 0:
        logging.info('%d classes missing integration tests in ui_write' % len(MISSING_INT))
    else:
        logging.info('all classes have integration tests')
    if verbose > 1:
        for cls in MISSING_INT:
            logging.info('%s missing integration tests defined in %s' % (cls, inspect.getfile(cls)))


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
