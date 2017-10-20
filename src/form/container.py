import abc
from six import with_metaclass
from operator import itemgetter
from .utils import docval, getargs

class Container(with_metaclass(abc.ABCMeta, object)):

    @classmethod
    def type_hierarchy(cls):
        return cls.__mro__

class Data(Container):

    @abc.abstractproperty
    def data(self):
        '''
        The data that is held by this Container
        '''
        ...

class DataRegion(Data):

    @abc.abstractproperty
    def data(self):
        '''
        The target data that this region applies to
        '''
        ...

    @abc.abstractproperty
    def region(self):
        '''
        The region that indexes into data e.g. slice or list of indices
        '''
        ...

class RegionSlicer(with_metaclass(abc.ABCMeta, object)):
    '''
    A class to control getting using a region
    '''

    @abc.abstractproperty
    def __getitem__(self, idx):
        pass

    @abc.abstractproperty
    def __len__(self):
        pass


class ListSlicer(RegionSlicer):

    @docval({'name': 'dataset', 'type': (list, tuple), 'doc': 'the HDF5 dataset to slice'},
            {'name': 'region', 'type': (list, tuple, slice), 'doc': 'the region reference to use to slice'})
    def __init__(self, **kwargs):
        self.__dataset, self.__region = getargs('dataset', 'region', kwargs)
        self.__read = None
        if isinstance(self.__region, slice):
            self.__getter = itemgetter(self.__region)
            self.__len = slice_len(self.__region)
        else:
            self.__getter = itemgetter(*self.__region)
            self.__len = len(self.__region)

    def __read_region(self):
        if not hasattr(self, '__read'):
            self.__read = self.__getter(self.__dataset)
            del self.__getter

    def __getitem__(self, idx):
        self.__read_region()
        getter = None
        if isinstance(idx, (list, tuple)):
            getter = itemgetter(*idx)
        else:
            return itemgetter(idx)
        return getter(self.__read)

    def __len__(self):
        return self.__len

@docval({'name': 'dataset', 'type': None, 'doc': 'the HDF5 dataset to slice'},
        {'name': 'region', 'type': None, 'doc': 'the region reference to use to slice'},
        is_method=False)
def get_region_slicer(**kwargs):
    dataset, region = getargs('dataset', 'region', kwargs)
    if isinstance(dataset, (list, tuple)):
        print(dataset)
        return ListSlicer(dataset, region)
    else:
        print('cant make region slicer', dataset)
