import numpy as np

from pynwb.retinotopy import ImagingRetinotopy, AxisMap, RetinotopyImage, FocalDepthImage, RetinotopyMap
from pynwb.testing import TestCase


class ImageRetinotopyConstructor(TestCase):

    def setUp(self):
        data = np.ones((2, 2))
        field_of_view = [1, 2]
        dimension = [1, 2]
        self.sign_map = RetinotopyMap('sign_map', data, field_of_view, dimension)
        self.axis_1_phase_map = AxisMap('axis_1_phase_map', data, field_of_view, 'unit', dimension)
        self.axis_1_power_map = AxisMap('axis_1_power_map', data, field_of_view, 'unit', dimension)
        self.axis_2_phase_map = AxisMap('axis_2_phase_map', data, field_of_view, 'unit', dimension)
        self.axis_2_power_map = AxisMap('axis_2_power_map', data, field_of_view, 'unit', dimension)
        self.axis_descriptions = ['altitude', 'azimuth']

        data = [[1, 1], [1, 1]]
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2]
        focal_depth = 1.0
        self.focal_depth_image = FocalDepthImage('focal_depth_image', data, bits_per_pixel, dimension, format,
                                                 field_of_view, focal_depth)
        self.vasculature_image = RetinotopyImage('vasculature_image', np.uint16(data), bits_per_pixel, dimension,
                                                 format, field_of_view)

    def test_init(self):
        """Test that ImagingRetinotopy constructor sets properties correctly."""
        msg = ('The ImagingRetinotopy class currently cannot be written to or read from a file. This is a known bug '
               'and will be fixed in a future release of PyNWB.')
        with self.assertWarnsWith(UserWarning, msg):
            ir = ImagingRetinotopy(self.sign_map, self.axis_1_phase_map, self.axis_1_power_map, self.axis_2_phase_map,
                                   self.axis_2_power_map, self.axis_descriptions, self.focal_depth_image,
                                   self.vasculature_image)
        self.assertEqual(ir.sign_map, self.sign_map)
        self.assertEqual(ir.axis_1_phase_map, self.axis_1_phase_map)
        self.assertEqual(ir.axis_1_power_map, self.axis_1_power_map)
        self.assertEqual(ir.axis_2_phase_map, self.axis_2_phase_map)
        self.assertEqual(ir.axis_2_power_map, self.axis_2_power_map)
        self.assertEqual(ir.axis_descriptions, self.axis_descriptions)
        self.assertEqual(ir.focal_depth_image, self.focal_depth_image)
        self.assertEqual(ir.vasculature_image, self.vasculature_image)

    def test_init_axis_descriptions_wrong_shape(self):
        """Test that creating a ImagingRetinotopy with a axis descriptions argument that is not 2 elements raises an
        error.
        """
        self.axis_descriptions = ['altitude', 'azimuth', 'extra']

        msg = "ImagingRetinotopy.__init__: incorrect shape for 'axis_descriptions' (got '(3,)', expected '(2,)')"
        with self.assertRaisesWith(ValueError, msg):
            ImagingRetinotopy(self.sign_map, self.axis_1_phase_map, self.axis_1_power_map, self.axis_2_phase_map,
                              self.axis_2_power_map, self.axis_descriptions, self.focal_depth_image,
                              self.vasculature_image)


class RetinotopyImageConstructor(TestCase):

    def test_init(self):
        """Test that RetinotopyImage constructor sets properties correctly."""
        data = [[1, 1], [1, 1]]
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2]
        image = RetinotopyImage('vasculature_image', data, bits_per_pixel, dimension, format, field_of_view)

        self.assertEqual(image.name, 'vasculature_image')
        self.assertEqual(image.data, data)
        self.assertEqual(image.bits_per_pixel, bits_per_pixel)
        self.assertEqual(image.dimension, dimension)
        self.assertEqual(image.format, format)
        self.assertEqual(image.field_of_view, field_of_view)

    def test_init_dimension_wrong_shape(self):
        """Test that creating a RetinotopyImage with a dimension argument that is not 2 elements raises an error."""
        data = [[1, 1], [1, 1]]
        bits_per_pixel = 8
        dimension = [3, 4, 5]
        format = 'raw'
        field_of_view = [1, 2]

        msg = "RetinotopyImage.__init__: incorrect shape for 'dimension' (got '(3,)', expected '(2,)')"
        with self.assertRaisesWith(ValueError, msg):
            RetinotopyImage('vasculature_image', data, bits_per_pixel, dimension, format, field_of_view)

    def test_init_fov_wrong_shape(self):
        """Test that creating a RetinotopyImage with a field of view argument that is not 2 elements raises an error."""
        data = [[1, 1], [1, 1]]
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2, 3]

        msg = "RetinotopyImage.__init__: incorrect shape for 'field_of_view' (got '(3,)', expected '(2,)')"
        with self.assertRaisesWith(ValueError, msg):
            RetinotopyImage('vasculature_image', data, bits_per_pixel, dimension, format, field_of_view)


class RetinotopyMapConstructor(TestCase):

    def test_init(self):
        """Test that RetinotopyMap constructor sets properties correctly."""
        data = np.ones((2, 2))
        field_of_view = [1, 2]
        dimension = [1, 2]
        map = RetinotopyMap('sign_map', data, field_of_view, dimension)

        self.assertEqual(map.name, 'sign_map')
        np.testing.assert_array_equal(map.data, data)
        self.assertEqual(map.field_of_view, field_of_view)
        self.assertEqual(map.dimension, dimension)


class AxisMapConstructor(TestCase):

    def test_init(self):
        """Test that AxisMap constructor sets properties correctly."""
        data = np.ones((2, 2))
        field_of_view = [1, 2]
        dimension = [1, 2]
        map = AxisMap('axis_1_phase', data, field_of_view, 'unit', dimension)

        self.assertEqual(map.name, 'axis_1_phase')
        np.testing.assert_array_equal(map.data, data)
        self.assertEqual(map.field_of_view, field_of_view)
        self.assertEqual(map.dimension, dimension)
        self.assertEqual(map.unit, 'unit')

    def test_init_dimension_wrong_shape(self):
        """Test that creating an AxisMap with a dimension argument that is not 2 elements raises an error."""
        data = np.ones((2, 2))
        field_of_view = [1, 2]
        dimension = [1, 2, 3]

        msg = "AxisMap.__init__: incorrect shape for 'dimension' (got '(3,)', expected '(2,)')"
        with self.assertRaisesWith(ValueError, msg):
            AxisMap('axis_1_phase', data, field_of_view, 'unit', dimension)

    def test_init_fov_wrong_shape(self):
        """Test that creating an AxisMap with a dimension argument that is not 2 elements raises an error."""
        data = np.ones((2, 2))
        field_of_view = [1, 2, 3]
        dimension = [1, 2]

        msg = "AxisMap.__init__: incorrect shape for 'field_of_view' (got '(3,)', expected '(2,)')"
        with self.assertRaisesWith(ValueError, msg):
            AxisMap('axis_1_phase', data, field_of_view, 'unit', dimension)


class FocalDepthImageConstructor(TestCase):

    def test_init(self):
        """Test that FocalDepthImage constructor sets properties correctly."""
        data = [[1, 1], [1, 1]]
        bits_per_pixel = 8
        dimension = [3, 4]
        format = 'raw'
        field_of_view = [1, 2]
        focal_depth = 1.0
        image = FocalDepthImage('focal_depth_image', data, bits_per_pixel, dimension, format, field_of_view,
                                focal_depth)

        self.assertEqual(image.name, 'focal_depth_image')
        self.assertEqual(image.data, data)
        self.assertEqual(image.bits_per_pixel, bits_per_pixel)
        self.assertEqual(image.dimension, dimension)
        self.assertEqual(image.format, format)
        self.assertEqual(image.field_of_view, field_of_view)
        self.assertEqual(image.focal_depth, focal_depth)
