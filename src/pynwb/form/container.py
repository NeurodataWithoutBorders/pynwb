import abc
from six import with_metaclass
from .utils import docval, getargs


class Container(with_metaclass(abc.ABCMeta, object)):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'parent', 'type': 'Container', 'doc': 'the Container that holds this Container', 'default': None},
            {'name': 'container_source', 'type': str, 'doc': 'the source of this container', 'default': None})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        if '/' in name:
            raise ValueError("name '" + name + "' cannot contain '/'")
        self.__name = name
        self.__parent = getargs('parent', kwargs)
        self.__container_source = getargs('container_source', kwargs)
        self.__children = list()
        self.__modified = True

    @property
    def modified(self):
        return self.__modified

    @docval({'name': 'modified', 'type': bool,
             'doc': 'whether or not this Container has been modified', 'default': True})
    def set_modified(self, **kwargs):
        modified = getargs('modified', kwargs)
        self.__modified = modified
        if modified and self.parent is not None:
            self.parent.set_modified()

    @property
    def children(self):
        return tuple(self.__children)

    @docval({'name': 'child', 'type': 'Container',
             'doc': 'the child Container for this Container', 'default': None})
    def add_child(self, **kwargs):
        child = getargs('child', kwargs)
        self.__children.append(child)
        self.set_modified()
        if not isinstance(child.parent, Container):
            child.parent = self

    @classmethod
    def type_hierarchy(cls):
        return cls.__mro__

    @property
    def name(self):
        '''
        The name of this Container
        '''
        return self.__name

    @property
    def container_source(self):
        '''
        The source of this Container
        '''
        return self.__container_source

    @container_source.setter
    def container_source(self, source):
        if self.__container_source is not None:
            raise Exception('cannot reassign container_source')
        self.__container_source = source

    @property
    def parent(self):
        '''
        The parent Container of this Container
        '''
        return self.__parent

    @parent.setter
    def parent(self, parent_container):
        if self.__parent is not None:
            if isinstance(self.__parent, Container):
                raise Exception('cannot reassign parent')
            else:
                if self.__parent.matches(parent_container):
                    self.__parent = parent_container
                else:
                    self.__parent.add_candidate(parent_container)
        else:
            self.__parent = parent_container


class Data(Container):

    @abc.abstractproperty
    def data(self):
        '''
        The data that is held by this Container
        '''
        pass

    def __nonzero__(self):
        return len(self.data) != 0


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
