from collections import Iterable
import numpy as np
from abc import ABCMeta, abstractmethod, abstractproperty
from six import with_metaclass
from .utils import docval, getargs, popargs, docval_macro
from operator import itemgetter
from .container import Data, DataRegion

from .validate.shapevalidator import ShapeValidator


@docval_macro('array_data')
class AbstractDataChunkIterator(with_metaclass(ABCMeta, object)):
    """
    Abstract iterator class used to iterate over DataChunks.

    Derived classes must ensure that all abstract methods and abstract properties are implemented, in
    particular, dtype, maxshape, __iter__, ___next__, recommended_chunk_shape, and recommended_data_shape.
    """

    @abstractmethod
    def __iter__(self):
        """Return the iterator object"""
        raise NotImplementedError("__iter__ not implemented for derived class")

    @abstractmethod
    def __next__(self):
        """
        Return the next data chunk or raise a StopIteration exception if all chunks have been retrieved.

        HINT: numpy.s_ provides a convenient way to generate index tuples using standard array slicing. This
        is often useful to define the DataChunk.selection of the current chunk

        :returns: DataChunk object with the data and selection of the current chunk
        :rtype: DataChunk
        """
        raise NotImplementedError("__next__ not implemented for derived class")

    @abstractmethod
    def recommended_chunk_shape(self):
        """

        :return: NumPy-style shape tuple describing the recommended shape for the chunks of the target
                 array or None. This may or may not be the same as the shape of the chunks returned in the
                 iteration process.
        """
        raise NotImplementedError("recommended_chunk_shape not implemented for derived class")

    @abstractmethod
    def recommended_data_shape(self):
        """
        Recommend the initial shape for the data array.

        This is useful in particular to avoid repeated resized of the target array when reading from
        this data iterator. This should typically be either the final size of the array or the known
        minimal shape of the array.

        :return: NumPy-style shape tuple indicating the recommended initial shape for the target array.
                 This may or may not be the final full shape of the array, i.e., the array is allowed
                 to grow. This should not be None.
        """
        raise NotImplementedError("recommended_data_shape not implemented for derived class")

    @abstractproperty
    def dtype(self):
        """
        Define the data type of the array

        :return: NumPy style dtype or otherwise compliant dtype string
        """
        raise NotImplementedError("dtype not implemented for derived class")

    @abstractproperty
    def maxshape(self):
        """
        Property describing the maximum shape of the data array that is being iterated over

        :return: NumPy-style shape tuple indicating the maxiumum dimensions up to which the dataset may be
                 resized. Axes with None are unlimited.
        """
        raise NotImplementedError("maxshape not implemented for derived class")


class DataChunkIterator(AbstractDataChunkIterator):
    """
    Custom iterator class used to iterate over chunks of data.

    This default implementation of AbstractDataChunkIterator accepts any iterable and assumes that we iterate over
    the first dimension of the data array. DataChunkIterator supports buffered read,
    i.e., multiple values from the input iterator can be combined to a single chunk. This is
    useful for buffered I/O operations, e.g., to improve performance by accumulating data
    in memory and writing larger blocks at once.
    """
    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'maxshape', 'type': tuple,
             'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions',
             'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def __init__(self, **kwargs):
        """Initialize the DataChunkIterator"""
        # Get the user parameters
        self.data, self.__maxshape, self.__dtype, self.buffer_size = getargs('data',
                                                                             'maxshape',
                                                                             'dtype',
                                                                             'buffer_size',
                                                                             kwargs)
        # Create an iterator for the data if possible
        self.__data_iter = iter(self.data) if isinstance(self.data, Iterable) else None
        self.__next_chunk = DataChunk(None, None)
        self.__first_chunk_shape = None
        # Determine the shape of the data if possible
        if self.__maxshape is None:
            # If the self.data object identifies it shape then use it
            if hasattr(self.data,  "shape"):
                self.__maxshape = self.data.shape
                # Avoid the special case of scalar values by making them into a 1D numpy array
                if len(self.__maxshape) == 0:
                    self.data = np.asarray([self.data, ])
                    self.__maxshape = self.data.shape
                    self.__data_iter = iter(self.data)
            # Try to get an accurate idea of __maxshape for other Python datastructures if possible.
            # Don't just callget_shape for a generator as that would potentially trigger loading of all the data
            elif isinstance(self.data, list) or isinstance(self.data, tuple):
                self.__maxshape = ShapeValidator.get_data_shape(self.data, strict_no_data_load=True)

        # If we have a data iterator, then read the first chunk
        if self.__data_iter is not None:  # and(self.__maxshape is None or self.__dtype is None):
            self._read_next_chunk()

        # If we still don't know the shape then try to determine the shape from the first chunk
        if self.__maxshape is None and self.__next_chunk.data is not None:
            data_shape = ShapeValidator.get_data_shape(self.__next_chunk.data)
            self.__maxshape = list(data_shape)
            try:
                self.__maxshape[0] = len(self.data)  # We use self.data here because self.__data_iter does not allow len
            except TypeError:
                self.__maxshape[0] = None
            self.__maxshape = tuple(self.__maxshape)

        # Determine the type of the data if possible
        if self.__next_chunk.data is not None:
            self.__dtype = self.__next_chunk.data.dtype
            self.__first_chunk_shape = ShapeValidator.get_data_shape(self.__next_chunk.data)

    @classmethod
    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'maxshape', 'type': tuple,
             'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions',
             'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def from_iterable(cls, **kwargs):
        return cls(**kwargs)

    def __iter__(self):
        """Return the iterator object"""
        return self

    def _read_next_chunk(self):
        """Read a single chunk from self.__data_iter and store the results in
           self.__next_chunk

        :returns: self.__next_chunk, i.e., the DataChunk object describing the next chunk
        """
        if self.__data_iter is not None:
            curr_next_chunk = []
            for i in range(self.buffer_size):
                try:
                    curr_next_chunk.append(next(self.__data_iter))
                except StopIteration:
                    pass
            next_chunk_size = len(curr_next_chunk)
            if next_chunk_size == 0:
                self.__next_chunk = DataChunk(None, None)
            else:
                self.__next_chunk.data = np.asarray(curr_next_chunk)
                if self.__next_chunk.selection is None:
                    self.__next_chunk.selection = slice(0, next_chunk_size)
                else:
                    self.__next_chunk.selection = slice(self.__next_chunk.selection.stop,
                                                        self.__next_chunk.selection.stop+next_chunk_size)
        else:
            self.__next_chunk = DataChunk(None, None)

        return self.__next_chunk

    def __next__(self):
        """Return the next data chunk or raise a StopIteration exception if all chunks have been retrieved.

        HINT: numpy.s_ provides a convenient way to generate index tuples using standard array slicing. This
        is often useful to define the DataChunkk.selection of the current chunk

        :returns: DataChunk object with the data and selection of the current chunk
        :rtype: DataChunk

        """
        # If we have not already read the next chunk, then read it now
        if self.__next_chunk.data is None:
            self._read_next_chunk()
        # If we do not have any next chunk
        if self.__next_chunk.data is None:
            raise StopIteration
        # If this is the first time we see a chunk then remember the size of the first chunk
        if self.__first_chunk_shape is None:
            self.__first_chunk_shape = self.__next_chunk.data.shape
        # Keep the next chunk we need to return
        curr_chunk = DataChunk(self.__next_chunk.data,
                               self.__next_chunk.selection)
        # Remove the data for the next chunk from our list since we are returning it here.
        # This is to allow the GarbageCollector to remmove the data when it goes out of scope and avoid
        # having 2 full chunks in memory if not necessary
        self.__next_chunk.data = None
        # Return the current next chunk
        return curr_chunk

    next = __next__

    @docval(returns='Tuple with the recommended chunk shape or None if no particular shape is recommended.')
    def recommended_chunk_shape(self):
        """Recommend a chunk shape.

        To optimize iterative write the chunk should be aligned with the common shape of chunks returned by __next__
        or if those chunks are too large, then a well-aligned subset of those chunks. This may also be
        any other value in case one wants to recommend chunk shapes to optimize read rather
        than write. The default implementation returns None, indicating no preferential chunking option."""
        return None

    @docval(returns='Recommended initial shape for the full data. This should be the shape of the full dataset' +
                    'if known beforehand or alternatively the minimum shape of the dataset. Return None if no ' +
                    'recommendation is available')
    def recommended_data_shape(self):
        """Recommend an initial shape of the data. This is useful when progressively writing data and
        we want to recommend and initial size for the dataset"""
        if self.__maxshape is not None:
            if np.all([i is not None for i in self.__maxshape]):
                return self.__maxshape
        return self.__first_chunk_shape

    @property
    def maxshape(self):
        return self.__maxshape

    @property
    def dtype(self):
        return self.__dtype


class DataChunk(object):
    """
    Class used to describe a data chunk. Used in DataChunkIterator to describe

    :ivar data: Numpy ndarray with the data value(s) of the chunk
    :ivar selection: Numpy index tuple describing the location of the chunk
    """
    @docval({'name': 'data', 'type': np.ndarray,
             'doc': 'Numpy array with the data value(s) of the chunk', 'default': None},
            {'name': 'selection', 'type': None,
             'doc': 'Numpy index tuple describing the location of the chunk', 'default': None})
    def __init__(self, **kwargs):
        self.data, self.selection = getargs('data', 'selection', kwargs)

    def __len__(self):
        if self.data is not None:
            return len(self.data)
        else:
            return 0


@docval_macro('data')
class DataIO(with_metaclass(ABCMeta, object)):

    @docval({'name': 'data', 'type': 'array_data', 'doc': 'the data to be written'})
    def __init__(self, **kwargs):
        data = popargs('data', kwargs)
        self.__data = data

    @property
    def data(self):
        return self.__data


class RegionSlicer(with_metaclass(ABCMeta, DataRegion)):
    '''
    A abstract base class to control getting using a region

    Subclasses must implement `__getitem__` and `__len__`
    '''

    @docval({'name': 'target', 'type': None, 'doc': 'the target to slice'},
            {'name': 'slice', 'type': None, 'doc': 'the region to slice'})
    def __init__(self, **kwargs):
        self.__target = getargs('target', kwargs)
        self.__slice = getargs('slice', kwargs)

    @property
    def data(self):
        return self.target

    @property
    def region(self):
        return self.slice

    @property
    def target(self):
        return self.__target

    @property
    def slice(self):
        return self.__slice

    @abstractproperty
    def __getitem__(self, idx):
        pass

    @abstractproperty
    def __len__(self):
        pass


class ListSlicer(RegionSlicer):

    @docval({'name': 'dataset', 'type': (list, tuple, Data), 'doc': 'the HDF5 dataset to slice'},
            {'name': 'region', 'type': (list, tuple, slice), 'doc': 'the region reference to use to slice'})
    def __init__(self, **kwargs):
        self.__dataset, self.__region = getargs('dataset', 'region', kwargs)
        super(ListSlicer, self).__init__(self.__dataset, self.__region)
        if isinstance(self.__region, slice):
            self.__getter = itemgetter(self.__region)
            self.__len = len(range(*self.__region.indices(len(self.__dataset))))
        else:
            self.__getter = itemgetter(*self.__region)
            self.__len = len(self.__region)

    def __read_region(self):
        if not hasattr(self, '_read'):
            self._read = self.__getter(self.__dataset)
            del self.__getter

    def __getitem__(self, idx):
        self.__read_region()
        getter = None
        if isinstance(idx, (list, tuple)):
            getter = itemgetter(*idx)
        else:
            getter = itemgetter(idx)
        return getter(self._read)

    def __len__(self):
        return self.__len
