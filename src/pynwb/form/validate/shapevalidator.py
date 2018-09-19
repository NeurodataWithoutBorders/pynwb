import numpy as np
from six import text_type, binary_type

from ..data_utils import DataChunkIterator


def __get_shape_helper(data):
    shape = list()
    if hasattr(data, '__len__'):
        shape.append(len(data))
        if len(data) and not isinstance(data[0], (text_type, binary_type)):
            shape.extend(__get_shape_helper(data[0]))
    return tuple(shape)


def get_shape(data):
    if isinstance(data, dict):
        return None
    elif hasattr(data, '__len__') and not isinstance(data, (text_type, binary_type)):
        return __get_shape_helper(data)
    else:
        return None


class ShapeValidator(object):
    """
    Helper class used to compare dimensions.

    This class consists mainly of a set of static helper functions used to check
    that the shape of arrays is compliant.
    """

    def __init__(self):
        """The typical use of this class is by calling static methods that return instances of ShapeValidatorResult"""
        pass

    @staticmethod
    def get_data_shape(data, strict_no_data_load=False):
        """
        Helper function used to determine the shape of the given array.

        :param data: Array for which we should determine the shape.
        :type data: List, numpy.ndarray, DataChunkIterator, any object that support __len__ or .shape.
        :param strict_no_data_load: In order to determin the shape of nested tuples and lists, this function
                    recursively inspects elements along the dimensions, assuming that the data has a regular,
                    rectangular shape. In the case of out-of-core iterators this means that the first item
                    along each dimensions would potentially be loaded into memory. By setting this option
                    we enforce that this does not happen, at the cost that we may not be able to determine
                    the shape of the array.
        :return: Tuple of ints indicating the size of known dimensions. Dimensions for which the size is unknown
                 will be set to None.
        """
        def __get_shape_helper(local_data):
            shape = list()
            if hasattr(local_data, '__len__'):
                shape.append(len(local_data))
                if len(local_data) and not isinstance(local_data[0], (text_type, binary_type)):
                    shape.extend(__get_shape_helper(local_data[0]))
            return tuple(shape)
        if isinstance(data, DataChunkIterator):
            return data.maxshape
        if hasattr(data, 'shape'):
            return data.shape
        if hasattr(data, '__len__') and not isinstance(data, (text_type, binary_type)):
            if not strict_no_data_load or (isinstance(data, list) or isinstance(data, tuple) or isinstance(data, set)):
                return __get_shape_helper(data)
            else:
                return None
        else:
            return None

    @staticmethod
    def assertEqualShape(data1,
                         data2,
                         axes1=None,
                         axes2=None,
                         name1=None,
                         name2=None,
                         ignore_undetermined=True):
        """
        Ensure that the shape of data1 and data2 match along the given dimensions

        :param data1: The first input array
        :type data1: List, Tuple, np.ndarray, DataChunkIterator etc.
        :param data2: The second input array
        :type data2: List, Tuple, np.ndarray, DataChunkIterator etc.
        :param name1: Optional string with the name of data1
        :param name2: Optional string with the name of data2
        :param axes1: The dimensions of data1 that should be matched to the dimensions of data2. Set to None to
                      compare all axes in order.
        :type axes1: int, Tuple of ints, List of ints, or None
        :param axes2: The dimensions of data2 that should be matched to the dimensions of data1. Must have
                      the same length as axes1. Set to None to compare all axes in order.
        :type axes1: int, Tuple of ints, List of ints, or None
        :param ignore_undetermined: Boolean indicating whether non-matching unlimited dimensions should be ignored,
                   i.e., if two dimension don't match because we can't determine the shape of either one, then
                   should we ignore that case or treat it as no match

        :return: Bool indicating whether the check passed and a string with a message about the matching process
        """
        # Create the base return object
        response = ShapeValidatorResult()
        # Determine the shape of the datasets
        response.shape1 = ShapeValidator.get_data_shape(data1)
        response.shape2 = ShapeValidator.get_data_shape(data2)
        # Determine the number of dimensions of the datasets
        num_dims_1 = len(response.shape1) if response.shape1 is not None else None
        num_dims_2 = len(response.shape2) if response.shape2 is not None else None
        # Determine the string names of the datasets
        n1 = name1 if name1 is not None else ("data1 at " + str(hex(id(data1))))
        n2 = name2 if name2 is not None else ("data2 at " + str(hex(id(data2))))
        # Determine the axes we should compare
        response.axes1 = list(range(num_dims_1)) if axes1 is None else ([axes1] if isinstance(axes1, int) else axes1)
        response.axes2 = list(range(num_dims_2)) if axes2 is None else ([axes2] if isinstance(axes2, int) else axes2)
        # Validate the array shape
        # 1) Check the number of dimensions of the arrays
        if (response.axes1 is None and response.axes2 is None) and num_dims_1 != num_dims_2:
            response.result = False
            response.error = 'NUM_DIMS_ERROR'
            response.message = response.SHAPE_ERROR[response.error]
            response.message += " %s is %sD and %s is %sD" % (n1, num_dims_1, n2, num_dims_2)
        # 2) Check that we have the same number of dimensions to compare on both arrays
        elif len(response.axes1) != len(response.axes2):
            response.result = False
            response.error = 'NUM_AXES_ERROR'
            response.message = response.SHAPE_ERROR[response.error]
            response.message += " Cannot compare axes %s with %s" % (str(response.axes1), str(response.axes2))
        # 3) Check that the datasets have sufficient numner of dimensions
        elif np.max(response.axes1) >= num_dims_1 or np.max(response.axes2) >= num_dims_2:
            response.result = False
            response.error = 'AXIS_OUT_OF_BOUNDS'
            response.message = response.SHAPE_ERROR[response.error]
            if np.max(response.axes1) >= num_dims_1:
                response.message += "Insufficient number of dimensions for %s -- Expected %i found %i" % \
                                    (n1, np.max(response.axes1)+1, num_dims_1)
            elif np.max(response.axes2) >= num_dims_2:
                response.message += "Insufficient number of dimensions for %s -- Expected %i found %i" % \
                                    (n2, np.max(response.axes2)+1, num_dims_2)
        # 4) Compare the length of the dimensions we should validate
        else:
            unmatched = []
            ignored = []
            for ax in zip(response.axes1, response.axes2):
                if response.shape1[ax[0]] != response.shape2[ax[1]]:
                    if ignore_undetermined and (response.shape1[ax[0]] is None or response.shape2[ax[1]] is None):
                        ignored.append(ax)
                    else:
                        unmatched.append(ax)
            response.unmatched = unmatched
            response.ignored = ignored

            # Check if everything checked out
            if len(response.unmatched) == 0:
                response.result = True
                response.error = None
                response.message = response.SHAPE_ERROR[response.error]
                if len(response.ignored) > 0:
                    response.message += " Ignored undetermined axes %s" % str(response.ignored)
            else:
                response.result = False
                response.error = 'AXIS_LEN_ERROR'
                response.message = response.SHAPE_ERROR[response.error]
                response.message += "Axes %s with size %s of %s did not match dimensions %s with sizes %s of %s." % \
                                    (str([un[0] for un in response.unmatched]),
                                     str([response.shape1[un[0]] for un in response.unmatched]),
                                     n1,
                                     str([un[1] for un in response.unmatched]),
                                     str([response.shape2[un[1]] for un in response.unmatched]),
                                     n2)
                if len(response.ignored) > 0:
                    response.message += " Ignored undetermined axes %s" % str(response.ignored)
        return response


class ShapeValidatorResult(object):
    """Class for storing results from validating the shape of multi-dimensional arrays.

    This class is used to store results generated by ShapeValidator

    :ivar result: Boolean indicating whether results matched or not
    :type result: bool
    :ivar message: Message indicating the result of the matching procedure
    :type messaage: str, None
    """
    SHAPE_ERROR = {None: 'All required axes matched',
                   'NUM_DIMS_ERROR': 'Unequal number of dimensions.',
                   'NUM_AXES_ERROR': "Unequal number of axes for comparison.",
                   'AXIS_OUT_OF_BOUNDS': "Axis index for comparison out of bounds.",
                   'AXIS_LEN_ERROR': "Unequal length of axes."}
    """
    Dict where the Keys are the type of errors that may have occurred during shape comparison and the
    values are strings with default error messages for the type.
    """

    def __init__(self, result=False, message=None, ignored=tuple(),
                 unmatched=tuple(), error=None, shape1=tuple(), shape2=tuple(),
                 axes1=tuple(), axes2=tuple()):
        """

        Parameters
        ----------
        result: bool
            Result of the shape validation
        message: str
            Message describing the result of the shape validation
        ignored: tuple
            Axes that have been ignored in the validaton process
        unmatched: tuple
            List of axes that did not match during shape validation
        error: str
            Error that may have occurred. One of ERROR_TYPE
        shape1: tuple
            Shape of the first array for comparison
        shape2: tuple
            Shape of the second array for comparison
        axes1: tuple
            Axes for the first array that should match
        axes2: tuple
            Axes for the second array that should match
        """
        self.result = result
        self.message = message
        self.ignored = ignored
        self.unmatched = unmatched
        self.error = error
        self.shape1 = shape1
        self.shape2 = shape2
        self.axes1 = axes1
        self.axes2 = axes2

    def __setattr__(self, key, value):
        """
        Overwrite to ensure that, e.g., error_message is not set to an illegal value.
        """
        if key == 'error':
            if value not in self.SHAPE_ERROR.keys():
                raise ValueError("Illegal error type. Error must be one of ShapeValidatorResult.SHAPE_ERROR: %s"
                                 % str(self.SHAPE_ERROR))
            else:
                super(ShapeValidatorResult, self).__setattr__(key, value)
        elif key in ['shape1', 'shape2', 'axes1', 'axes2', 'ignored', 'unmatched']:  # Make sure we sore tuples
            super(ShapeValidatorResult, self).__setattr__(key, tuple(value))
        else:
            super(ShapeValidatorResult, self).__setattr__(key, value)

    def __getattr__(self, item):
        """
        Overwrite to allow dynamic retrieval of the default message
        """
        if item == 'default_message':
            return self.SHAPE_ERROR[self.error]
        return self.__getattribute__(item)
