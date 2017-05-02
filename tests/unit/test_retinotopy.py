import unittest

from pynwb.retinotopy import ImagingRetinotopy, amap, aimage

import numpy as np


class ImageRetinotopyConstructor(unittest.TestCase):

    def test_init(self):
        data = list()
        field_of_view = [1, 2, 3]
        dimension = [1, 2, 3]
        sign_map = amap(data, field_of_view, 'unit', dimension)
        axis_1_phase_map = amap(data, field_of_view, 'unit', dimension)
        axis_1_power_map = amap(data, field_of_view, 'unit', dimension)
        axis_2_phase_map = amap(data, field_of_view, 'unit', dimension)
        axis_2_power_map = amap(data, field_of_view, 'unit', dimension)
        axis_descriptions = ['altitude', 'azimuth']

        data = list()
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2, 3]
        focal_depth = 1.0
        focal_depth_image = aimage(data, bits_per_pixel, dimension, format, field_of_view, focal_depth)
        vasculature_image = aimage(data, bits_per_pixel, dimension, format, field_of_view, focal_depth)

        ir = ImagingRetinotopy('test_ir', sign_map, axis_1_phase_map, axis_1_power_map, axis_2_phase_map, axis_2_power_map, axis_descriptions, focal_depth_image, vasculature_image)
        self.assertEqual(ir.source, 'test_ir')
        self.assertEqual(ir.sign_map, sign_map)
        self.assertEqual(ir.axis_1_phase_map, axis_1_phase_map)
        self.assertEqual(ir.axis_1_power_map, axis_1_power_map)
        self.assertEqual(ir.axis_2_phase_map, axis_2_phase_map)
        self.assertEqual(ir.axis_2_power_map, axis_2_power_map)
        self.assertEqual(ir.axis_descriptions, axis_descriptions)
        self.assertEqual(ir.focal_depth_image, focal_depth_image)
        self.assertEqual(ir.vasculature_image, vasculature_image)

if __name__ == '__main__':
    unittest.main()

