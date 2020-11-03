# import numpy as np
#
# from pynwb.retinotopy import ImagingRetinotopy, AxisMap, RetinotopyImage, FocalDepthImage, RetinotopyMap
# from pynwb.testing import AcquisitionH5IOMixin, TestCase
#
#
# class TestImagingRetinotopy(AcquisitionH5IOMixin, TestCase):
#
#     def setUpContainer(self):
#         """ Return the test ImagingRetinotopy to read/write """
#         data = np.ones((2, 2))
#         field_of_view = [1, 2]
#         dimension = [1, 2]
#         sign_map = RetinotopyMap('sign_map', data, field_of_view, dimension)
#         axis_1_phase_map = AxisMap('axis_1_phase_map', data, field_of_view, 'unit', dimension)
#         axis_1_power_map = AxisMap('axis_1_power_map', data, field_of_view, 'unit', dimension)
#         axis_2_phase_map = AxisMap('axis_2_phase_map', data, field_of_view, 'unit', dimension)
#         axis_2_power_map = AxisMap('axis_2_power_map', data, field_of_view, 'unit', dimension)
#         axis_descriptions = ['altitude', 'azimuth']
#
#         data = [[1, 1], [1, 1]]
#         bits_per_pixel = 8
#         dimension = [3, 4]
#         format = 'raw'
#         field_of_view = [1, 2]
#         focal_depth = 1.0
#         focal_depth_image = FocalDepthImage('focal_depth_image', data, bits_per_pixel, dimension, format,
#                                             field_of_view, focal_depth)
#         vasculature_image = RetinotopyImage('vasculature_image', np.uint16(data), bits_per_pixel, dimension, format,
#                                             field_of_view)
#
#         return ImagingRetinotopy(sign_map, axis_1_phase_map, axis_1_power_map, axis_2_phase_map,
#                                  axis_2_power_map, axis_descriptions, focal_depth_image,
#                                  vasculature_image)
