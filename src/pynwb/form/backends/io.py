from abc import ABCMeta, abstractmethod
from ..build import BuildManager
from ..build import GroupBuilder
from ..utils import docval, getargs, popargs
from ..container import Container
from six import with_metaclass


class FORMIO(with_metaclass(ABCMeta, object)):
    @docval({'name': 'manager', 'type': BuildManager,
             'doc': 'the BuildManager to use for I/O', 'default': None},
            {"name": "source", "type": str,
             "doc": "the source of container being built i.e. file path", 'default': None})
    def __init__(self, **kwargs):
        self.__manager = getargs('manager', kwargs)
        self.__built = dict()
        self.__source = getargs('source', kwargs)
        self.open()

    @property
    def manager(self):
        '''The BuildManager this FORMIO is using'''
        return self.__manager

    @property
    def source(self):
        '''The source of the container being read/written i.e. file path'''
        return self.__source

    @docval(returns='the Container object that was read in', rtype=Container)
    def read(self, **kwargs):
        f_builder = self.read_builder()
        container = self.__manager.construct(f_builder)
        return container

    @docval({'name': 'container', 'type': Container, 'doc': 'the Container object to write'})
    def write(self, **kwargs):
        container = popargs('container', kwargs)
        f_builder = self.__manager.build(container, source=self.__source)
        self.write_builder(f_builder, **kwargs)

    @abstractmethod
    @docval(returns='a GroupBuilder representing the read data', rtype='GroupBuilder')
    def read_builder(self):
        ''' Read data and return the GroupBuilder represention '''
        pass

    @abstractmethod
    @docval({'name': 'builder', 'type': GroupBuilder, 'doc': 'the GroupBuilder object representing the Container'})
    def write_builder(self, **kwargs):
        ''' Write a GroupBuilder representing an Container object '''
        pass

    @abstractmethod
    def open(self):
        ''' Open this FORMIO object for writing of the builder '''
        pass

    @abstractmethod
    def close(self):
        ''' Close this FORMIO object to further reading/writing'''
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
