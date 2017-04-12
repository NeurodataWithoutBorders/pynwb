from abc import ABCMeta, abstractmethod
from .build import BuildManager
from .build import GroupBuilder
from ..core import docval
from ..file import NWBFile

class NWBReader(object, metaclass=ABCMeta):

    @abstractmethod
    @docval(returns='a GroupBuilder representing the NWB Dataset', rtype='GroupBuilder')
    def read_builder(self):
        ''' Read an NWB Dataset and return the GroupBuilder represention '''
        pass

class NWBWriter(object, metaclass=ABCMeta):

    @abstractmethod
    @docval({'name': 'builder', 'type': GroupBuilder, 'doc': 'the GroupBuilder object representing the NWBFile'})
    def write_builder(self, **kwargs):
        ''' Write a GroupBuilder representing an NWBFile object '''
        pass

class NWBIO(object):
    @docval({'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager to use for I/O', 'default': None})
    def __init__(self, **kwargs):
        self.__manager = getargs('manager', kwargs)
        if self.__manager is None:
            from pynwb.io import TYPE_MAP
            self.__manager = BuildManager(TYPE_MAP)
        self.__built = dict()

    @docval({'name': 'reader', 'type': NWBReader, 'doc': 'the NWBReader object that handles reading'},
            returns='the NWBFile object', rtype=NWBFile)
    def read(self, **kwargs):
        reader = kwargs['reader']
        f_builder = reader.read_builder()
        nwb_file = self.__manager.construct(f_builder)
        return nwb_file

    @docval({'name': 'nwb_file', 'type': NWBFile, 'doc': 'the NWBFile object to write'},
            {'name': 'writer', 'type': NWBWriter, 'doc': 'the NWBWriter object that handles writing'})
    def write(self, **kwargs):
        nwb_file, writer = getargs('nwb_file', 'writer', kwargs)
        f_builder = self.__manager.build(nwb_file)
        writer.write_builder(f_builder)
