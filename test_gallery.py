"""Test that the Sphinx Gallery files run without warnings or errors.

See tox.ini for usage.
"""
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

TOTAL = 0
FAILURES = 0
ERRORS = 0


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
        except Exception:
            print(traceback.format_exc())
            FAILURES += 1
            ERRORS += 1

def clean_up_tests():
    # remove files generated from running example files
    files_to_remove = [
        "ecog.extensions.yaml",
        "ecog.namespace.yaml",
        "test_multicontainerinterface.extensions.yaml",
        "test_multicontainerinterface.namespace.yaml",
    ]
    for f in files_to_remove:
        for name in glob.glob(f):
            if os.path.exists(name):
                os.remove(name)

    shutil.rmtree("zarr_tutorial.nwb.zarr")

def main():
    run_example_tests()
    run_example_ros3_tests()

    final_message = "Ran %s tests" % TOTAL
    exitcode = 0
    if ERRORS > 0 or FAILURES > 0:
        exitcode = 1
        _list = list()
        if ERRORS > 0:
            _list.append("errors=%d" % ERRORS)
        if FAILURES > 0:
            _list.append("failures=%d" % FAILURES)
        final_message = "%s - FAILED (%s)" % (final_message, ",".join(_list))
    else:
        final_message = "%s - OK" % final_message

    logging.info(final_message)

    return exitcode


if __name__ == "__main__":
    sys.exit(main())
