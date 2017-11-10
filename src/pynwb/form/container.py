import abc
from six import with_metaclass


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
        pass


class DataRegion(Data):

    @abc.abstractproperty
    def data(self):
        '''
        The target data that this region applies to
        '''
        pass

    @abc.abstractproperty
    def region(self):
        '''
        The region that indexes into data e.g. slice or list of indices
        '''
        pass
