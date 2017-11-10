from abc import ABCMeta, abstractmethod
import six

from .utils import docval
from .data_utils import AbstractDataChunkIterator, DataChunkIterator, DataChunk


class NotYetExhausted(Exception):
    pass


@six.add_metaclass(ABCMeta)
class DataChunkProcessor(AbstractDataChunkIterator):

    @docval({'name': 'data', 'type': DataChunkIterator, 'doc': 'the DataChunkIterator to analyze'})
    def __init__(self, **kwargs):
        """Initalize the DataChunkIterator"""
        # Get the user parameters
        self.__dci = getargs('data', kwargs)  # noqa: F821

    def __next__(self):
        try:
            dc = self.__dci.__next__()
        except StopIteration as e:
            self.__done = True
            raise e
        self.process_data_chunk(dc)
        return dc

    def __iter__(self):
        return iter(self.__dci)

    def recommended_chunk_shape(self):
        return self.__dci.recommended_chunk_shape()

    def recommended_data_shape(self):
        return self.__dci.recommended_data_shape()

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
        args, kwargs = fmt_docval_args(DataChunkProcessor.__init__, kwargs)  # noqa: F821
        super(NumSampleCounter, self).__init__(*args, **kwargs)
        self.__sample_count = 0

    @docval({'name': 'data_chunk', 'type': DataChunk, 'doc': 'a chunk to process'})
    def process_data_chunk(self, **kwargs):
        dc = getargs('data_chunk', kwargs)  # noqa: F821
        self.__sample_count += len(dc)

    @docval(returns='the result of processing this stream')
    def compute_final_result(self, **kwargs):
        return self.__sample_count
