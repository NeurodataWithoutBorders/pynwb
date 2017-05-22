import unittest
import sys

result = unittest.TextTestRunner().run(unittest.defaultTestLoader.discover("tests/unit"))

if result.errors or result.failures:
    sys.exit(1)
