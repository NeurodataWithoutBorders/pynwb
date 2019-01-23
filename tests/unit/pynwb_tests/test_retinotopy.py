import unittest

import numpy as np

from pynwb.retinotopy import ImagingRetinotopy, AxisMap, AImage


class ImageRetinotopyConstructor(unittest.TestCase):

    def test_init(self):
        data = np.ones((2, 2))
        field_of_view = [1, 2, 3]
        dimension = [1, 2, 3]
        sign_map = AxisMap('sign_map', data, field_of_view, 'unit', dimension)
        axis_1_phase_map = AxisMap('axis_1_phase', data, field_of_view, 'unit', dimension)
        axis_1_power_map = AxisMap('axis_1_power', data, field_of_view, 'unit', dimension)
        axis_2_phase_map = AxisMap('axis_2_phase', data, field_of_view, 'unit', dimension)
        axis_2_power_map = AxisMap('axis_2_power', data, field_of_view, 'unit', dimension)
        axis_descriptions = ['altitude', 'azimuth']

        data = list()
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2, 3]
        focal_depth = 1.0
        focal_depth_image = AImage('focal_depth_image', data, bits_per_pixel,
                                   dimension, format, field_of_view, focal_depth)
        vasculature_image = AImage('vasculature', data, bits_per_pixel,
                                   dimension, format, field_of_view, focal_depth)

        ir = ImagingRetinotopy(sign_map, axis_1_phase_map, axis_1_power_map, axis_2_phase_map,
                               axis_2_power_map, axis_descriptions, focal_depth_image, vasculature_image)
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
