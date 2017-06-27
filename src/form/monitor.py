from abc import ABCMeta, abstractmethod

from .utils import DataChunkIterator


class NotYetExhausted(Exception):
    pass

class DataChunkProcessor(DataChunkIterator, metaclass=ABCMeta):


    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'max_shape', 'type': tuple,
             'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions',
             'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def __init__(self, **kwargs):
        """Initalize the DataChunkIterator"""
        # Get the user parameters
        args, kwargs = fmt_docval_args(DataChunkIterator.__init__, kwargs)
        super(DataChunkIterator, self).__init__(*args, **kwargs)

    def __next__(self):
        try:
            dc = super(DataChunkIterator, self).__next__()
        except StopIteration as e:
            self.__done = True
            raise e
        self.process_data_chunk(dc)

    def get_final_result(self, **kwargs):
        ''' Return the result of processing data fed by this DataChunkIterator '''
        if not self.__done:
            raise NotYetExhausted()
        return self.compute_final_result()


    @abstractmethod
    @docval({'name': 'data_chunk', 'type': DataChunk, 'doc': 'a chunk to process'})
    def process_data_chunk(self, **kwargs):
        ''' This method should take in a DataChunk,
            and process it.
        '''
        pass

    @abstractmethod
    @docval(returns='the result of processing this stream')
    def compute_final_result(self, **kwargs):
        ''' Return the result of processing this stream
            Should raise NotYetExhaused exception
        '''
        pass

class NumSampleCounter(DataChunkProcessor):

    def __init__(self, **kwargs):
        args, kwargs = fmt_docval_args(DataChunkProcessor.__init__, kwargs)
        self.__sample_count = 0

    @docval({'name': 'data_chunk', 'type': DataChunk, 'doc': 'a chunk to process'})
    def process_data_chunk(self, **kwargs):
        dc = getargs('data_chunk', kwargs)
        self.__sample_count += len(dc)

