import unittest

from pynwb.retinotopy import ImageRetinotopy

import numpy as np


class ImageRetinotopyConstructor(unittest.TestCase):

    def test_init(self):
        lt = list()
        ir = ImageRetinotopy('test_ir', lt, lt, lt, lt, lt, lt, lt, lt)
        self.assertEqual(ir.source, 'test_ir')


if __name__ == '__main__':
    unittest.main()