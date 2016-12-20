import sys
import os.path
sys.path.append(os.path.abspath("src"))
import unittest
unittest.TextTestRunner().run(unittest.defaultTestLoader.discover("tests"))
