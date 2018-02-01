from collections import Iterable
from h5py import RegionReference

from .form.utils import docval, getargs, ExtenderMeta, call_docval_func, popargs, get_docval, fmt_docval_args
from .form import Container, Data, DataRegion, get_region_slicer

from . import CORE_NAMESPACE, register_class
from six import with_metaclass


def _not_parent(arg):
    return arg['name'] != 'parent'


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


class LabelledDict(dict):
    '''
    A dict wrapper class for aggregating Timeseries
    from the standard locations
    '''

    @docval({'name': 'label', 'type': str, 'doc': 'the TimeSeries type ('})
    def __init__(self, **kwargs):
        label = getargs('label', kwargs)
        self.__label = label

    @property
    def label(self):
        return self.__label


class NWBBaseType(with_metaclass(ExtenderMeta)):
    '''The base class to any NWB types.

    The purpose of this class is to provide a mechanism for representing hierarchical
    relationships in neurodata.
    '''

    __nwbfields__ = tuple()

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        parent, container_source = getargs('parent', 'container_source', kwargs)
        super(NWBBaseType, self).__init__()
        self.__fields = dict()
        self.__parent = None
        self.__name = getargs('name', kwargs)
        if parent:
            self.parent = parent
        self.__container_source = container_source

    @property
    def name(self):
        return self.__name

    @property
    def container_source(self):
        '''The source of this Container e.g. file name or table
        '''
        return self.__container_source

    @property
    def fields(self):
        return self.__fields

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

    @staticmethod
    def _getter(nwbfield):
        def _func(self):
            return self.fields.get(nwbfield)
        return _func

    @staticmethod
    def _setter(nwbfield):
        def _func(self, val):
            if nwbfield in self.fields:
                msg = "can't set attribute '%s' -- already set" % nwbfield
                raise AttributeError(msg)
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

        if len(bases) and 'NWBContainer' in globals() and issubclass(bases[-1], NWBContainer) \
           and bases[-1].__nwbfields__ is not cls.__nwbfields__:
                new_nwbfields = list(cls.__nwbfields__)
                new_nwbfields[0:0] = bases[-1].__nwbfields__
                cls.__nwbfields__ = tuple(new_nwbfields)
        for f in cls.__nwbfields__:
            if not hasattr(cls, f):
                setattr(cls, f, property(cls._getter(f), cls._setter(f)))


@register_class('NWBContainer', CORE_NAMESPACE)
class NWBContainer(NWBBaseType, Container):

    __nwbfields__ = ('source',
                     'help')

    @docval({'name': 'source', 'type': str, 'doc': 'a description of where this NWBContainer came from'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(NWBContainer, self).__init__, kwargs)
        self.source = getargs('source', kwargs)

    def _to_dict(self, arg, label="NULL"):
        return_dict = LabelledDict(label)
        if arg is None:
            return return_dict
        else:
            for i in arg:
                assert i.name is not None  # If a container doesn't have a name, it gets lost!
                assert i.name not in return_dict
                return_dict[i.name] = i
            return return_dict


@register_class('NWBDataInterface', CORE_NAMESPACE)
class NWBDataInterface(NWBContainer):
    pass


@register_class('NWBData', CORE_NAMESPACE)
class NWBData(NWBBaseType, Data):

    __nwbfields__ = ('help',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': (Iterable, Data), 'doc': 'the source of the data'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(NWBData, self).__init__, kwargs)
        self.__data = getargs('data', kwargs)

    @property
    def data(self):
        return self.__data


class NWBTable(NWBData):

    @docval({'name': 'columns', 'type': (list, tuple), 'doc': 'a list of the columns in this table'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': Iterable, 'doc': 'the source of the data', 'default': list()},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        self.__columns = tuple(popargs('columns', kwargs))
        call_docval_func(super(NWBTable, self).__init__, kwargs)

    @property
    def columns(self):
        return self.__columns

    @docval({'name': 'values', 'type': dict, 'doc': 'the values for each column'})
    def add_row(self, **kwargs):
        values = getargs('values', kwargs)
        if not isinstance(self.data, list):
            msg = 'Cannot append row to %s' % type(self.data)
            raise ValueError(msg)
        self.data.append(tuple(values[col] for col in self.columns))

    @docval({'name': 'kwargs', 'type': dict, 'doc': 'the column to query by'})
    def query(self, **kwargs):
        '''
        Query a table
        '''
        raise NotImplementedError('query')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


# diamond inheritence
class NWBTableRegion(NWBData, DataRegion):
    '''
    A class for representing regions i.e. slices or indices into an NWBTable
    '''

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'table', 'type': NWBTable, 'doc': 'the ElectrodeTable this region applies to'},
            {'name': 'region', 'type': (slice, list, tuple, RegionReference), 'doc': 'the indices of the table'})
    def __init__(self, **kwargs):
        table, region = getargs('table', 'region', kwargs)
        self.__table = table
        self.__region = region
        name = getargs('name', kwargs)
        super(NWBTableRegion, self).__init__(name, table)
        self.__regionslicer = get_region_slicer(self.__table.data, self.__region)

    @property
    def table(self):
        '''The ElectrodeTable this region applies to'''
        return self.__table

    @property
    def region(self):
        '''The indices into table'''
        return self.__region

    def __len__(self):
        return len(self.__regionslicer)

    def __getitem__(self, idx):
        return self.__regionslicer[idx]


class MultiTSInterface(NWBDataInterface):
    '''
    A class for dynamically defining a API classes that
    represent NWBDataInterfaces that contain multiple TimeSeries
    of the same type

    To use, extend this class, and create a dictionary as a class
    attribute with the following keys:

    'add' to name the method for adding TimeSeries instances
    'create' to name the method fo creating TimeSeries instances
    'ts_attr' to name the attribute that stores the TimeSeries instances
    'ts_type' to provide the TimeSeries object type

    See LFP or Position for an example of how to use this.
    '''

    @staticmethod
    def __add_article(noun):
        if noun[0] in ('aeiouAEIOU'):
            return 'an %s' % noun
        return 'a %s' % noun

    @classmethod
    def __make_add(cls, func_name, attr_name, ts_type):
        doc = "Add %s to this %s" % (cls.__add_article(ts_type.__name__), cls.__name__)

        @docval({'name': attr_name, 'type': ts_type, 'doc': 'the %s to add' % ts_type.__name__},
                func_name=func_name, doc=doc)
        def _func(self, **kwargs):
            ts = getargs(attr_name, kwargs)
            ts.parent = self
            d = getattr(self, attr_name)
            if ts.name in d:
                msg = "'%s' already exists" % ts.name
                raise ValueError(msg)
            d[ts.name] = ts
        return _func

    @classmethod
    def __make_create(cls, func_name, add_name, ts_type):
        doc = "Create %s and add it to this %s" % \
                       (cls.__add_article(ts_type.__name__), cls.__name__)

        @docval(*filter(_not_parent, get_docval(ts_type.__init__)), func_name=func_name, doc=doc,
                returns="the %s object that was created" % ts_type.__name__, rtype=ts_type)
        def _func(self, **kwargs):
            cargs, ckwargs = fmt_docval_args(ts_type.__init__, kwargs)
            ret = ts_type(*cargs, **ckwargs)
            getattr(self, add_name)(ret)
            return ret
        return _func

    @classmethod
    def __make_constructor(cls, attr_name, add_name, ts_type):
        @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
                {'name': attr_name, 'type': (list, dict, ts_type),
                 'doc': '%s to store in this interface' % ts_type.__name__, 'default': dict()},
                {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': cls.__name__},
                func_name='__init__')
        def _func(self, **kwargs):
            source, ts = popargs('source', attr_name, kwargs)
            super(MultiTSInterface, self).__init__(source, **kwargs)
            setattr(self, attr_name, dict())
            add = getattr(self, add_name)
            if isinstance(ts, ts_type):
                add(ts)
            elif isinstance(ts, list):
                for tmp in ts:
                    add(tmp)
            else:
                for tmp in ts.values():
                    add(tmp)
        return _func

    @ExtenderMeta.pre_init
    def __build_class(cls, name, bases, classdict):
        '''
        This classmethod will be called during class declaration in the metaclass to automatically
        create setters and getters for NWB fields that need to be exported
        '''
        if not hasattr(cls, '__clsconf__'):
            return
        if not isinstance(cls.__clsconf__, dict):
            raise TypeError("'__clsconf__' must be of type dict")

        add = cls.__clsconf__['add']
        create = cls.__clsconf__['create']
        ts_attr = cls.__clsconf__['ts_attr']
        ts_type = cls.__clsconf__['ts_type']
        if not hasattr(cls, ts_attr):
            getter = cls._getter(ts_attr)
            doc = "a dictionary containing the %s in this %s" % (ts_type.__name__, cls.__name__)
            setattr(cls, ts_attr, property(getter, cls._setter(ts_attr), None, doc))
        setattr(cls, add, cls.__make_add(add, ts_attr, ts_type))
        setattr(cls, create, cls.__make_create(create, add, ts_type))
        setattr(cls, '__init__', cls.__make_constructor(ts_attr, add, ts_type))
