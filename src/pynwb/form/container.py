import abc
from six import with_metaclass
from .utils import docval, getargs


class Container(with_metaclass(abc.ABCMeta, object)):

    @docval({'name': 'parent', 'type': 'Container', 'doc': 'the Container that holds this Container', 'default': None})
    def __init__(self, **kwargs):
        self.__parent = getargs('parent', kwargs)

    @classmethod
    def type_hierarchy(cls):
        return cls.__mro__

    @property
    def parent(self):
        '''The parent NWBContainer of this NWBContainer
        '''
        return self.__parent

    @parent.setter
    def parent(self, parent_container):
        if self.__parent is not None:
            raise Exception('cannot reassign parent')
        self.__parent = parent_container


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
