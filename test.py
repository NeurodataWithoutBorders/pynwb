import unittest2 as unittest
import sys
import argparse

import pynwb

parser = argparse.ArgumentParser('python test.py [options]')
parser.set_defaults(verbosity=1)
parser.add_argument('-v', '--verbose', const=2, dest='verbosity', action='store_const', help='run in verbose mode')
parser.add_argument('-q', '--quiet', const=0, dest='verbosity', action='store_const', help='run in verbose mode')

args = parser.parse_args()

result = unittest.TextTestRunner(verbosity=args.verbosity).run(unittest.defaultTestLoader.discover("tests/unit"))

type_map = pynwb.get_global_type_map()
import imp
name = 'unit'
imp_result = imp.find_module(name, ['tests'])
mod = imp.load_module(name, imp_result[0], imp_result[1], imp_result[2])

d = mod.integration.ui_write.base.container_tests
missing = list()
for cls in type_map.get_container_classes():
    if cls not in d:
        missing.append(cls)
sys.stdout.write('%d classes missing integration tests in ui_write\n' % len(missing))
if args.verbosity > 1:
    for cls in missing:
        sys.stdout.write('%s missing integration tests\n' % cls)

if result.errors or result.failures:
    sys.exit(1)
