from abc import abstractmethod

from pynwb.core import ExtenderMeta
from pynwb.core import docval, getargs
from collections import Iterable
import numpy as np


class BaseObjectHandler(object, metaclass=ExtenderMeta):

    _property = "__item_property__"
    @ExtenderMeta.post_init
    def __gather_procedures(cls, name, bases, classdict):
        cls.procedures = dict()
        for name, func in filter(lambda tup: hasattr(tup[1], cls._property), cls.__dict__.items()):
            # NOTE: We need to get the original functions from the class dict since
            # the attributes added to cls after calling type will be processed.
            # i.e. staticmethod objects lose their attributes in the binding process
            # But, we need to get the function after it's been bound, since
            # staticmethod objects are not callable (after staticmethods are processed
            # by type, they are bound to the class as a function)
            cls.procedures[getattr(func, cls._property)] = getattr(cls, name)


    @classmethod
    @abstractmethod
    def get_object_properties(cls, obj):
        """Defines how message properties gets extracted. This
           must be implemented in extending classes, and it
           must return a list of properties.
        """
        ...

    @classmethod
    def get_object_representation(cls, obj):
        """Defines how messages get rendered before passing them
           into procedures. By default, the object itself is returned
        """
        return obj

    def process(self, obj):
        properties = self.get_object_properties(obj)
        ret = list()
        for prop in properties:
            val = None
            if prop in self.procedures:
                func = self.procedures[prop]
                val = func(self.get_object_representation(obj))
            ret.append(val)
        return ret

    @classmethod
    def procedure(cls, prop):
        """Decorator for adding procedures within definition
           of derived classes.
        """
        def _dec(func):
            func2 = staticmethod(func)
            setattr(func2, cls._property, prop)
            return func2
        return _dec

    @classmethod
    def procedure_ext(cls, prop):
        """Decorator for adding additional procedures to
           class procedures from outside class definition.
        """
        def _dec(func):
            cls.procedures[prop] = func
            setattr(cls, func.__name__, func)
            return func
        return _dec


class DataChunkIterator(object):
    """Custom iterator class used to iterate over chunks of data.

    Derived classes must ensure that self.shape and self.dtype are set properly.
    define the self.max_shape property describing the maximum shape of the array.
    In addition, derived classes must implement the __next__ method (or overwrite __read_next_chunk__
    if the default behavior of __next__ should be reused). The __next__ method must return
    in each iteration 1) a numpy array with the data values for the chunk and 2) a numpy-compliant index tuple
    describing where the chunk is located within the complete data.  HINT: numpy.s_ provides a
    convenient way to generate index tuples using standard array slicing. There are
    a number of additional functions that one can overwrite to customize behavior, e.g,
    the recommended_chunk_size() or recommended_

    The default implementation accepts any iterable and assumes that we iterate over
    the first dimension of the data array. The default implemention supports buffered read,
    i.e., multiple values from the input iterator can be combined to a single chunk. This is
    useful for buffered I/O operations, e.g., to improve performance by accumulating data
    in memory and writing larger blocks at once.
    """
    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'max_shape', 'type': tuple, 'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions', 'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def __init__(self, **kwargs):
        """Initalize the DataChunkIterator"""
        # Get the user parameters
        self.data, self.max_shape, self.dtype, self.buffer_size = getargs('data',
                                                                          'max_shape',
                                                                          'dtype' ,
                                                                          'buffer_size',
                                                                          kwargs)
        # Create an iterator for the data if possible
        self.__data_iter = iter(self.data) if isinstance(self.data, Iterable) else None
        self.__next_chunk = None
        self.__next_chunk_location = None
        # Determine the shape of the data if possible
        if self.max_shape is None:
            # If the self.data object identifies it shape then use it
            if hasattr(self.data,  "shape"):
                self.max_shape = self.data.shape
                # Avoid the special case of scalar values by making them into a 1D numpy array
                if len(self.max_shape) == 0:
                    self.data = np.asarray([self.data,])
                    self.max_shape = self.data.shape
                    self.__data_iter = iter(self.data)
            # Try to get an accurate idea of max_shape for other Python datastructures if possible.
            # Don't just call __get_shape for a generator as that would potentially trigger loading of all the data
            elif isinstance(self.data, list) or isinstance(self.data, tuple):
                self.max_shape = self.__get_shape(self.data)


            # If we have a data iterator, then read the first chunk
            if self.__data_iter is not None:
                self.__read_next_chunk__()
            # Determine the recommended chunk shape
            self.__recommended_chunk_shape = self.__get_shape(self.__next_chunk) if self.__next_chunk is not None else None

            # If we still don't know the shape then try to determine the shape from the first chunk
            if self.max_shape is None and self.__next_chunk is not None:
                data_shape = self.__get_shape(self.__next_chunk)
                self.max_shape =  list(data_shape)
                self.max_shape[0] = None
                self.max_shape = tuple(self.max_shape)
        # Determine the type of the data if possibe
        if self.__next_chunk is not None:
            self.dtype = self.__next_chunk.dtype

    def __iter__(self):
        """Return the iterator object"""
        return self

    def __read_next_chunk__(self):
        """Read a single chunk from self.__data_iter and store the results in
           self.__next_chunk and self.__chunk_location"""
        if self.__data_iter is not None:
            self.__next_chunk = []
            for i in range(self.buffer_size):
                try:
                    self.__next_chunk.append(next(self.__data_iter))
                except StopIteration:
                    pass
            next_chunk_size = len(self.__next_chunk)
            if next_chunk_size == 0:
                self.__next_chunk = None
                self.__next_chunk_location = None
            else:
                self.__next_chunk = np.asarray(self.__next_chunk)
                if self.__next_chunk_location is None:
                    self.__next_chunk_location = slice(0, next_chunk_size)
                else:
                    self.__next_chunk_location = slice(self.__next_chunk_location.stop,
                                                       self.__next_chunk_location.stop+next_chunk_size)

        else:
            self.__next_chunk = None
            self.__next_chunk_location = None

        return self.__next_chunk, self.__next_chunk_location

    @docval(returns="The following two items must be returned: \n" + \
                    "* Numpy array (or scalar) with the data for the next chunk \n" +\
                    "* Numpy-compliant index tuple describing the location of the chunk in the complete array. " +\
                    "HINT: numpy.s_ provides a convenient way to generate index tuples using standard array slicing.")
    def __next__(self):
        """Return the next data chunk or raise a StopIteration exception if all chunks have been retrieved."""
        if self.__next_chunk is None:
            raise StopIteration
        else:
            curr_chunk = self.__next_chunk
            curr_location = self.__next_chunk_location
            self.__read_next_chunk__()
            return curr_chunk, curr_location


    @staticmethod
    def __get_shape(data):
        """Internal helper function used to determin the shape of data objects"""
        def __get_shape_helper(data):
            shape = list()
            if hasattr(data, '__len__'):
                shape.append(len(data))
                if len(data) and not isinstance(data[0], str):
                    shape.extend(__get_shape_helper(data[0]))
            return tuple(shape)
        if hasattr(data, '__len__') and not isinstance(data, str):
            return __get_shape_helper(data)
        else:
            return None

    @docval(returns='Tuple with the recommended chunk shape or None if no particular shape is recommended.')
    def recommended_chunk_shape(self):
        """Recommend a chunk shape. This will typcially be the most common shape of chunk returned by __next__
        but may also be some other value in case one wants to recommend chunk shapes to optimize read rather
        than write."""
        return self.__recommended_chunk_shape

    @docval(returns='Recommended initial shape for the full data. This should be the shape of the full dataset' +\
                    'if known beforehand or alternatively the minimum shape of the dataset. Return None if no ' +\
                    'recommendation is available')
    def recommended_data_shape(self):
        """Recommend an initial shape of the data. This is useful when progressively writing data and
        we want to recommend and inital size for the dataset"""
        if self.max_shape is not None:
            if np.all([i is not None for i in self.max_shape]):
                return self.max_shape
            else:
                return self.__recommended_chunk_shape
        else:
            return None

