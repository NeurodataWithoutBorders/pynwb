import unittest2 as unittest
import sys

import argparse

parser = argparse.ArgumentParser('python test.py [options]')
parser.set_defaults(verbosity=1)
parser.add_argument('-v', '--verbose', const=2, dest='verbosity', action='store_const', help='run in verbose mode')
parser.add_argument('-q', '--quiet', const=0, dest='verbosity', action='store_const', help='run in verbose mode')

args = parser.parse_args()

result = unittest.TextTestRunner(verbosity=args.verbosity).run(unittest.defaultTestLoader.discover("tests/unit"))

if result.errors or result.failures:
    sys.exit(1)
