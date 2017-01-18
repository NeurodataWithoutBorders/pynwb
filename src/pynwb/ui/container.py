from ..core import docval, getargs


class NWBContainer(object):
    '''The base class to any NWB types.
    
    The purpose of this class is to provide a mechanism for representing hierarchical
    relationships in neurodata.
    '''
    
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
        return self.__parent
    
    @parent.setter
    def parent(self, parent_container):
        if self.__parent:
            self.__parent.__subcontainers.remove(self)
        self.__parent = parent_container
        parent_container.__subcontainers.append(self)

def nwbproperties(*args, **kwargs):
    '''Create settable and gettable properties that can be exported to NWB files
       
       Decorate NWBContainers with this.
    '''
    def get_func(prop_name):
        def _getter_func(self):
            return self.fields.get(prop_name)
        return _getter_func

    def set_func(prop_name):
        def _setter_func(self, val):
            self.fields[prop_name] = val
        return _setter_func

    def inner(cls):
        classdict = dict(cls.__dict__)

        nwb_fields = list()
        for bs in cls.__bases__:
            if hasattr(bs, '__nwbfields__'):
                nwb_fields.extend(getattr(bs, '__nwbfields__'))
        for arg in args:
            getter = get_func(arg)
            setter = set_func(arg)
            classdict[arg] = property(getter, setter)
            nwb_fields.append(arg)
        for arg in kwargs:
            getter = lambda cls: kwargs[arg]
            classdict[arg] = property(getter)
            nwb_fields.append(arg)

        nwb_fields = tuple(nwb_fields)
        #classdict['nwb_fields'] = classmethod(lambda cls: nwb_fields)
        classdict['__nwbfields__'] = nwb_fields
        return type(cls.__name__, cls.__bases__, classdict)
    return inner
