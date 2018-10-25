import unittest2 as unittest

from pynwb.form.data_utils import ShapeValidatorResult, DataChunkIterator, assertEqualShape
import numpy as np


class ShapeValidatorTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_array_all_dimensions_match(self):
        # Test match
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(10).reshape(2, 5)
        res = assertEqualShape(d1, d2)
        self.assertTrue(res.result)
        self.assertIsNone(res.error)
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (2, 5))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1))

    def test_array_dimensions_mismatch(self):
        # Test unmatched
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(10).reshape(5, 2)
        res = assertEqualShape(d1, d2)
        self.assertFalse(res.result)
        self.assertEqual(res.error, 'AXIS_LEN_ERROR')
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ((0, 0), (1, 1)))
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1))

    def test_array_unequal_number_of_dimensions(self):
        # Test unequal num dims
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(5, 2, 2)
        res = assertEqualShape(d1, d2)
        self.assertFalse(res.result)
        self.assertEquals(res.error, 'NUM_AXES_ERROR')
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2, 2))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1, 2))

    def test_array_unequal_number_of_dimensions_check_one_axis_only(self):
        # Test unequal num dims compare one axis
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(2, 5, 2)
        res = assertEqualShape(d1, d2, 0, 0)
        self.assertTrue(res.result)
        self.assertIsNone(res.error)
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (2, 5, 2))
        self.assertTupleEqual(res.axes1, (0,))
        self.assertTupleEqual(res.axes2, (0,))

    def test_array_unequal_number_of_dimensions_check_multiple_axesy(self):
        # Test unequal num dims compare multiple axes
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(5, 2, 2)
        res = assertEqualShape(d1, d2, [0, 1], [1, 0])
        self.assertTrue(res.result)
        self.assertIsNone(res.error)
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2, 2))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (1, 0))

    def test_array_unequal_number_of_axes_for_comparison(self):
        # Test unequal num axes for comparison
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(5, 2, 2)
        res = assertEqualShape(d1, d2, [0, 1], 1)
        self.assertFalse(res.result)
        self.assertEquals(res.error, "NUM_AXES_ERROR")
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2, 2))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (1,))

    def test_array_axis_index_out_of_bounds_single_axis(self):
        # Test too large frist axis
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(5, 2, 2)
        res = assertEqualShape(d1, d2, 4, 1)
        self.assertFalse(res.result)
        self.assertEquals(res.error, 'AXIS_OUT_OF_BOUNDS')
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2, 2))
        self.assertTupleEqual(res.axes1, (4,))
        self.assertTupleEqual(res.axes2, (1,))

    def test_array_axis_index_out_of_bounds_mutilple_axis(self):
        # Test too large second axis
        d1 = np.arange(10).reshape(2, 5)
        d2 = np.arange(20).reshape(5, 2, 2)
        res = assertEqualShape(d1, d2, [0, 1], [5, 0])
        self.assertFalse(res.result)
        self.assertEquals(res.error, 'AXIS_OUT_OF_BOUNDS')
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (5, 2, 2))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (5, 0))

    def test_DataChunkIterators_match(self):
        # Compare data chunk iterators
        d1 = DataChunkIterator(data=np.arange(10).reshape(2, 5))
        d2 = DataChunkIterator(data=np.arange(10).reshape(2, 5))
        res = assertEqualShape(d1, d2)
        self.assertTrue(res.result)
        self.assertIsNone(res.error)
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (2, 5))
        self.assertTupleEqual(res.shape2, (2, 5))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1))

    def test_DataChunkIterator_ignore_undetermined_axis(self):
        # Compare data chunk iterators with undetermined axis (ignore axis)
        d1 = DataChunkIterator(data=np.arange(10).reshape(2, 5), maxshape=(None, 5))
        d2 = DataChunkIterator(data=np.arange(10).reshape(2, 5))
        res = assertEqualShape(d1, d2, ignore_undetermined=True)
        self.assertTrue(res.result)
        self.assertIsNone(res.error)
        self.assertTupleEqual(res.ignored, ((0, 0),))
        self.assertTupleEqual(res.unmatched, ())
        self.assertTupleEqual(res.shape1, (None, 5))
        self.assertTupleEqual(res.shape2, (2, 5))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1))

    def test_DataChunkIterator_error_on_undetermined_axis(self):
        # Compare data chunk iterators with undetermined axis (error on undetermined axis)
        d1 = DataChunkIterator(data=np.arange(10).reshape(2, 5), maxshape=(None, 5))
        d2 = DataChunkIterator(data=np.arange(10).reshape(2, 5))
        res = assertEqualShape(d1, d2, ignore_undetermined=False)
        self.assertFalse(res.result)
        self.assertEquals(res.error, 'AXIS_LEN_ERROR')
        self.assertTupleEqual(res.ignored, ())
        self.assertTupleEqual(res.unmatched, ((0, 0),))
        self.assertTupleEqual(res.shape1, (None, 5))
        self.assertTupleEqual(res.shape2, (2, 5))
        self.assertTupleEqual(res.axes1, (0, 1))
        self.assertTupleEqual(res.axes2, (0, 1))


class ShapeValidatorResultTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_message(self):
        temp = ShapeValidatorResult()
        temp.error = 'AXIS_LEN_ERROR'
        self.assertEquals(temp.default_message, ShapeValidatorResult.SHAPE_ERROR[temp.error])

    def test_set_error_to_illegal_type(self):
        temp = ShapeValidatorResult()
        with self.assertRaises(ValueError):
            temp.error = 'MY_ILLEGAL_ERROR_TYPE'

    def test_ensure_use_of_tuples_during_asignment(self):
        temp = ShapeValidatorResult()
        temp_d = [1, 2]
        temp_cases = ['shape1', 'shape2', 'axes1', 'axes2', 'ignored', 'unmatched']
        for var in temp_cases:
            setattr(temp, var, temp_d)
            self.assertIsInstance(getattr(temp, var), tuple,  var)


if __name__ == '__main__':
    unittest.main()
