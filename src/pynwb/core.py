from form.utils import docval, getargs, ExtenderMeta
from form import Container


def set_parents(container, parent):
    if isinstance(container, list):
        for c in container:
            if c.parent is None:
                c.parent = parent
        ret = container
    else:
        ret = [container]
        if container.parent is None:
            container.parent = parent
    return ret

class NWBContainer(Container, metaclass=ExtenderMeta):
    '''The base class to any NWB types.

    The purpose of this class is to provide a mechanism for representing hierarchical
    relationships in neurodata.
    '''


    __nwbfields__ = tuple()


    @docval({'name': 'parent', 'type': 'NWBContainer', 'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object, 'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        parent, container_source = getargs('parent', 'container_source', kwargs)
        self.__fields = dict()
        self.__subcontainers = list()
        self.__parent = None
        if parent:
            self.parent = parent
        self.__container_source = container_source

    @property
    def neurodata_type(self):
        return self.__class__.__name__

    @property
    def namespace(cls):
        return getattr(cls, '_%s__namespace' % cls.__name__)

    @property
    def container_source(self):
        '''The source of this Container e.g. file name or table
        '''
        return self.__container_source

    @property
    def fields(self):
        return self.__fields

    @property
    def subcontainers(self):
        return self.__subcontainers

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
        parent_container.__subcontainers.append(self)

    @staticmethod
    def __getter(nwbfield):
        def _func(self):
            return self.fields.get(nwbfield)
        return _func

    @staticmethod
    def __setter(nwbfield):
        def _func(self, val):
            self.fields[nwbfield] = val
        return _func

    @ExtenderMeta.pre_init
    def __gather_nwbfields(cls, name, bases, classdict):
        '''
        This classmethod will be called during class declaration in the metaclass to automatically
        create setters and getters for NWB fields that need to be exported
        '''
        if not isinstance(cls.__nwbfields__, tuple):
            raise TypeError("'__nwbfields__' must be of type tuple")

        if len(bases) and 'NWBContainer' in globals() and issubclass(bases[-1], NWBContainer) and bases[-1].__nwbfields__ is not cls.__nwbfields__:
                new_nwbfields = list(cls.__nwbfields__)
                new_nwbfields[0:0] = bases[-1].__nwbfields__
                cls.__nwbfields__ = tuple(new_nwbfields)
        for f in cls.__nwbfields__:
            if not hasattr(cls, f):
                setattr(cls, f, property(cls.__getter(f), cls.__setter(f)))

    # TODO: do something to handle when multiple derived classes have the same name
    __all_subclasses = dict()

    @ExtenderMeta.pre_init
    def __register_subclass(cls, name, bases, classdict):
        cls.__all_subclasses[name] = cls

    @classmethod
    def get_subclass(cls, neurodata_type):
        return cls.__all_subclasses.get(neurodata_type, None)


