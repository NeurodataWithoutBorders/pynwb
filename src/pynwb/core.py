from h5py import RegionReference
import numpy as np

from .form.utils import docval, getargs, ExtenderMeta, call_docval_func, popargs, get_docval, fmt_docval_args
from .form import Container, Data, DataRegion, get_region_slicer

from . import CORE_NAMESPACE, register_class
from six import with_metaclass, iteritems


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

    def __getitem__(self, args):
        key = args
        if '==' in args:
            key, val = args.split("==")
            key = key.strip()
            val = val.strip()
            if key != 'name':
                ret = list()
                for item in self.values():
                    if getattr(item, key, None) == val:
                        ret.append(item)
                return ret if len(ret) else None
            key = val
        return super(LabelledDict, self).__getitem__(key)


def prepend_string(string, prepend='    '):
    return prepend + prepend.join(string.splitlines(True))


def nwb_repr(nwb_object, verbose=True):
    try:
        template = "{} {}\nFields:\n""".format(getattr(nwb_object, 'name'), type(nwb_object))

        if verbose:
            for k, v in iteritems(nwb_object.fields):
                template += "  {}:\n".format(k)
                if isinstance(v, list):
                    for item in v:
                        template += prepend_string(nwb_repr(item, verbose=False)) + '\n'
                else:
                    template += prepend_string(str(v)) + '\n'
        else:
            for field in ('description', ):
                template += "  {}:\n".format(field)
                template += prepend_string(str(getattr(nwb_object, field)))+'\n'

        return template
    except AttributeError:
        return str(nwb_object)


class NWBBaseType(with_metaclass(ExtenderMeta, Container)):
    '''The base class to any NWB types.

    The purpose of this class is to provide a mechanism for representing hierarchical
    relationships in neurodata.
    '''

    __nwbfields__ = tuple()

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'parent', 'type': Container,
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        parent, container_source = getargs('parent', 'container_source', kwargs)
        call_docval_func(super(NWBBaseType, self).__init__, kwargs)
        self.__fields = dict()

    @property
    def fields(self):
        return self.__fields

    @classmethod
    def subtypes(cls):
        """
        Get list of all subtypes of this class
        :return: Python set with all the subclasses of the current class
        """
        return set(cls.__subclasses__()).union(
            [subclass for current_subclass in cls.__subclasses__()
               for subclass in current_subclass.subtypes()])

    @staticmethod
    def _transform_arg(nwbfield):
        tmp = nwbfield
        if isinstance(tmp, dict):
            if 'name' not in tmp:
                raise ValueError("must specify 'name' if using dict in __nwbfields__")
        else:
            tmp = {'name': tmp}
        return tmp

    @classmethod
    def _getter(cls, nwbfield):
        doc = nwbfield.get('doc')
        name = nwbfield['name']

        def nwbbt_getter(self):
            return self.fields.get(name)

        setattr(nwbbt_getter, '__doc__', doc)
        return nwbbt_getter

    @classmethod
    def _setter(cls, nwbfield):
        name = nwbfield['name']

        def nwbbt_setter(self, val):
            if val is None:
                return
            if name in self.fields:
                msg = "can't set attribute '%s' -- already set" % name
                raise AttributeError(msg)
            self.fields[name] = val

        return nwbbt_setter

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
        new_nwbfields = list()
        docs = {dv['name']: dv['doc'] for dv in get_docval(cls.__init__)}
        for f in cls.__nwbfields__:
            pconf = cls._transform_arg(f)
            pname = pconf['name']
            pconf.setdefault('doc', docs.get(pname))
            if not hasattr(cls, pname):
                setattr(cls, pname, property(cls._getter(pconf), cls._setter(pconf)))
            new_nwbfields.append(pname)
        cls.__nwbfields__ = tuple(new_nwbfields)

    def __str__(self):
        return nwb_repr(self)


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

    @classmethod
    def _setter(cls, nwbfield):
        super_setter = NWBBaseType._setter(nwbfield)
        ret = super_setter
        if isinstance(nwbfield, dict) and nwbfield.get('child', False):

            def nwbdi_setter(self, val):
                super_setter(self, val)
                if val is not None:
                    if isinstance(val, (tuple, list)):
                        pass
                    elif isinstance(val, dict):
                        val = val.values()
                    else:
                        val = [val]
                    for v in val:
                        self.add_child(v)

            ret = nwbdi_setter
        return ret

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

    @docval(*get_docval(NWBContainer.__init__))
    def __init__(self, **kwargs):
        call_docval_func(super(NWBDataInterface, self).__init__, kwargs)


@register_class('NWBData', CORE_NAMESPACE)
class NWBData(NWBBaseType, Data):

    __nwbfields__ = ('help',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('array_data', 'data', Data), 'doc': 'the source of the data'},
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

    def __len__(self):
        return len(self.__data)

    def __getitem__(self, args):
        return self.data[args]

    def append(self, arg):
        if isinstance(self.data, list):
            self.data.append(arg)
        elif isinstance(self.data, np.ndarray):
            self.__data = np.append(self.__data, [arg])
        else:
            msg = "NWBData cannot append to object of type '%s'" % type(self.__data)
            raise ValueError(msg)

    def extend(self, arg):
        if isinstance(self.data, list):
            self.data.extend(arg)
        elif isinstance(self.data, np.ndarray):
            self.__data = np.append(self.__data, [arg])
        else:
            msg = "NWBData cannot extend object of type '%s'" % type(self.__data)
            raise ValueError(msg)


@register_class('VectorData', CORE_NAMESPACE)
class VectorData(NWBData):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(VectorData, self).__init__, kwargs)


@register_class('VectorIndex', CORE_NAMESPACE)
class VectorIndex(NWBData):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorIndex'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a 1D dataset containing indexes that apply to VectorData object'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(VectorIndex, self).__init__, kwargs)


class IndexedVector(object):

    @docval({'name': 'data', 'type': VectorData,
             'doc': 'the VectorData to maintain'},
            {'name': 'index', 'type': VectorIndex,
             'doc': 'a VectorIndex object that indexes this VectorData', 'default': None})
    def __init__(self, **kwargs):
        self.__data = popargs('data', kwargs)
        self.__index = popargs('index', kwargs)

    def add_vector(self, arg):
        before = len(self.__data)
        self.__data.extend(arg)
        rs = get_region_slicer(self.__data, slice(before, before+len(arg)))
        self.__index.append(rs)
        return len(self.__index)-1

    def get_vector(self, arg):
        return self.__index[arg][:]


@register_class('ElementIdentifiers', CORE_NAMESPACE)
class ElementIdentifiers(NWBData):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this ElementIdentifiers'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'a 1D dataset containing identifiers'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ElementIdentifiers, self).__init__, kwargs)


class NWBTable(NWBData):
    '''
    Subclasses should specify the class attribute \_\_columns\_\_.

    This should be a list of dictionaries with the following keys:
    ``'name'`` - the column name
    ``'type'`` - the type of data in this column
    ``'doc'``  - a brief description of what gets stored in this column

    For reference, this list of dictionaries will be used with docval to autogenerate
    the ``add_row`` method for adding data to this table.

    If \_\_columns\_\_ is not specified, no custom ``add_row`` method will be added.

    The class attribute __defaultname__ can also be set to specify a default name
    for the table class. If \_\_defaultname\_\_ is not specified, then ``name`` will
    need to be specified when the class is instantiated.
    '''

    @ExtenderMeta.pre_init
    def __build_table_class(cls, name, bases, classdict):
        if hasattr(cls, '__columns__'):
            columns = getattr(cls, '__columns__')

            idx = dict()
            for i, col in enumerate(columns):
                idx[col['name']] = i
            setattr(cls, '__colidx__', idx)

            if cls.__init__ == bases[-1].__init__:     # check if __init__ is overridden
                name = {'name': 'name', 'type': str, 'doc': 'the name of this table'}
                defname = getattr(cls, '__defaultname__', None)
                if defname is not None:
                    name['default'] = defname

                @docval(name,
                        {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the data in this table',
                         'default': list()})
                def __init__(self, **kwargs):
                    name, data = getargs('name', 'data', kwargs)
                    colnames = [i['name'] for i in columns]
                    super(cls, self).__init__(colnames, name, data)

                setattr(cls, '__init__', __init__)

            if cls.add_row == bases[-1].add_row:     # check if add_row is overridden

                @docval(*columns)
                def add_row(self, **kwargs):
                    return super(cls, self).add_row(kwargs)

                setattr(cls, 'add_row', add_row)

    @docval({'name': 'columns', 'type': (list, tuple), 'doc': 'a list of the columns in this table'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the source of the data', 'default': list()},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        self.__columns = tuple(popargs('columns', kwargs))
        self.__col_index = {name: idx for idx, name in enumerate(self.__columns)}
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
        ret = len(self.data)
        self.data.append(tuple(values[col] for col in self.columns))
        return ret

    def which(self, **kwargs):
        '''
        Query a table
        '''
        if len(kwargs) != 1:
            raise ValueError("only one column can be queried")
        colname, value = kwargs.popitem()
        idx = self.__colidx__.get(colname)
        if idx is None:
            msg = "no '%s' column in %s" % (colname, self.__class__.__name__)
            raise KeyError(msg)
        ret = list()
        for i in range(len(self.data)):
            row = self.data[i]
            row_val = row[idx]
            if row_val == value:
                ret.append(i)
        return ret

    def __len__(self):
        return len(self.data)

    def __getitem__(self, args):
        idx = args
        col = None
        if isinstance(args, tuple):
            idx = args[1]
            if isinstance(args[0], str):
                col = self.__col_index.get(args[0])
            elif isinstance(args[0], int):
                col = args[0]
            else:
                raise KeyError('first argument must be a column name or index')
            return self.data[idx][col]
        elif isinstance(args, str):
            col = self.__col_index.get(args)
            if col is None:
                raise KeyError(args)
            return [row[col] for row in self.data]
        else:
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


class MultiContainerInterface(NWBDataInterface):
    '''
    A class for dynamically defining a API classes that
    represent NWBDataInterfaces that contain multiple Containers
    of the same type

    To use, extend this class, and create a dictionary as a class
    attribute with the following keys:

    * 'add' to name the method for adding Container instances

    * 'create' to name the method fo creating Container instances

    * 'get' to name the method for getting Container instances

    * 'attr' to name the attribute that stores the Container instances

    * 'type' to provide the Container object type

    See LFP or Position for an example of how to use this.
    '''

    @docval(*get_docval(NWBDataInterface.__init__))
    def __init__(self, **kwargs):
        call_docval_func(super(MultiContainerInterface, self).__init__, kwargs)
        if isinstance(self.__clsconf__, dict):
            attr_name = self.__clsconf__['attr']
            self.fields[attr_name] = LabelledDict(attr_name)
        else:
            for d in self.__clsconf__:
                attr_name = d['attr']
                self.fields[attr_name] = LabelledDict(attr_name)

    @staticmethod
    def __add_article(noun):
        if noun[0] in ('aeiouAEIOU'):
            return 'an %s' % noun
        return 'a %s' % noun

    @classmethod
    def __make_get(cls, func_name, attr_name, container_type):
        doc = "Get %s from this %s" % (cls.__add_article(container_type.__name__), cls.__name__)

        @docval({'name': 'name', 'type': str, 'doc': 'the name of the %s' % container_type.__name__,
                 'default': None}, rtype=container_type, returns='the %s with the given name' % container_type.__name__,
                func_name=func_name, doc=doc)
        def _func(self, **kwargs):
            name = getargs('name', kwargs)
            d = getattr(self, attr_name)
            ret = None
            if name is None:
                if len(d) > 1:
                    msg = "more than one element in %s of %s '%s' -- must specify a name" % \
                          (attr_name, cls.__name__, self.name)
                    raise ValueError(msg)
                elif len(d) == 0:
                    msg = "%s of %s '%s' is empty" % (attr_name, cls.__name__, self.name)
                    raise ValueError(msg)
                elif len(d) == 1:
                    for v in d.values():
                        ret = v
            else:
                ret = d.get(name)
                if ret is None:
                    msg = "'%s' not found in %s of %s '%s'" % (name, attr_name, cls.__name__, self.name)
                    raise KeyError(msg)
            return ret

        return _func

    @classmethod
    def __make_add(cls, func_name, attr_name, container_type):
        doc = "Add %s to this %s" % (cls.__add_article(container_type.__name__), cls.__name__)

        @docval({'name': attr_name, 'type': (list, tuple, dict, container_type),
                 'doc': 'the %s to add' % container_type.__name__},
                func_name=func_name, doc=doc)
        def _func(self, **kwargs):
            container = getargs(attr_name, kwargs)
            if isinstance(container, container_type):
                containers = [container]
            elif isinstance(container, dict):
                containers = container.values()
            else:
                containers = container
            d = getattr(self, attr_name)
            for tmp in containers:
                self.add_child(tmp)
                if tmp.name in d:
                    msg = "'%s' already exists in '%s'" % (tmp.name, self.name)
                    raise ValueError(msg)
                d[tmp.name] = tmp
            return container
        return _func

    @classmethod
    def __make_create(cls, func_name, add_name, container_type):
        doc = "Create %s and add it to this %s" % \
                       (cls.__add_article(container_type.__name__), cls.__name__)

        @docval(*filter(_not_parent, get_docval(container_type.__init__)), func_name=func_name, doc=doc,
                returns="the %s object that was created" % container_type.__name__, rtype=container_type)
        def _func(self, **kwargs):
            cargs, ckwargs = fmt_docval_args(container_type.__init__, kwargs)
            ret = container_type(*cargs, **ckwargs)
            getattr(self, add_name)(ret)
            return ret
        return _func

    @classmethod
    def __make_constructor(cls, attr_name, add_name, container_type):
        @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
                {'name': attr_name, 'type': (list, tuple, dict, container_type),
                 'doc': '%s to store in this interface' % container_type.__name__, 'default': dict()},
                {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': cls.__name__},
                func_name='__init__')
        def _func(self, **kwargs):
            source, container = popargs('source', attr_name, kwargs)
            super(cls, self).__init__(source, **kwargs)
            add = getattr(self, add_name)
            add(container)
        return _func

    @classmethod
    def __make_getitem(cls, attr_name, container_type):
        doc = "Get %s from this %s" % (cls.__add_article(container_type.__name__), cls.__name__)

        @docval({'name': 'name', 'type': str, 'doc': 'the name of the %s' % container_type.__name__,
                 'default': None}, rtype=container_type, returns='the %s with the given name' % container_type.__name__,
                func_name='__getitem__', doc=doc)
        def _func(self, **kwargs):
            name = getargs('name', kwargs)
            d = getattr(self, attr_name)
            if len(d) == 0:
                msg = "%s '%s' is empty" % (cls.__name__, self.name)
                raise ValueError(msg)
            if len(d) > 1 and name is None:
                msg = "more than one %s in this %s -- must specify a name" % container_type.__name__, cls.__name__
                raise ValueError(msg)
            ret = None
            if len(d) == 1:
                for v in d.values():
                    ret = v
            else:
                ret = d.get(name)
                if ret is None:
                    msg = "'%s' not found in %s '%s'" % (name, cls.__name__, self.name)
                    raise KeyError(msg)
            return ret

        return _func

    @classmethod
    def __make_setter(cls, nwbfield, add_name):

        @docval({'name': 'val', 'type': (list, tuple, dict), 'doc': 'the sub items to add', 'default': None})
        def nwbbt_setter(self, **kwargs):
            val = getargs('val', kwargs)
            if val is None:
                return
            getattr(self, add_name)(val)

        return nwbbt_setter

    @ExtenderMeta.pre_init
    def __build_class(cls, name, bases, classdict):
        '''
        This classmethod will be called during class declaration in the metaclass to automatically
        create setters and getters for NWB fields that need to be exported
        '''
        if not hasattr(cls, '__clsconf__'):
            return
        multi = False
        if isinstance(cls.__clsconf__, dict):
            clsconf = [cls.__clsconf__]
        elif isinstance(cls.__clsconf__, list):
            multi = True
            clsconf = cls.__clsconf__
        else:
            raise TypeError("'__clsconf__' must be a dict or a list of dicts")

        for i, d in enumerate(clsconf):
            # get add method name
            add = d.get('add')
            if add is None:
                msg = "MultiContainerInterface subclass '%s' is missing 'add' key in __clsconf__" % cls.__name__
                if multi:
                    msg += " at element %d" % i
                raise ValueError(msg)

            # get container attribute name
            attr = d.get('attr')
            if attr is None:
                msg = "MultiContainerInterface subclass '%s' is missing 'attr' key in __clsconf__" % cls.__name__
                if multi:
                    msg += " at element %d" % i
                raise ValueError(msg)

            # get container type
            container_type = d.get('type')
            if container_type is None:
                msg = "MultiContainerInterface subclass '%s' is missing 'type' key in __clsconf__" % cls.__name__
                if multi:
                    msg += " at element %d" % i
                raise ValueError(msg)

            # create property with the name given in 'attr'
            if not hasattr(cls, attr):
                aconf = cls._transform_arg(attr)
                getter = cls._getter(aconf)
                doc = "a dictionary containing the %s in this %s container" % (container_type.__name__, cls.__name__)
                setattr(cls, attr, property(getter, cls.__make_setter(aconf, add), None, doc))

            # create the add method
            setattr(cls, add, cls.__make_add(add, attr, container_type))

            # create the constructor, only if it has not been overriden
            # i.e. it is the same method as the parent class constructor
            if cls.__init__ == MultiContainerInterface.__init__:
                setattr(cls, '__init__', cls.__make_constructor(attr, add, container_type))

            # get create method name
            create = d.get('create')
            if create is not None:
                setattr(cls, create, cls.__make_create(create, add, container_type))

            get = d.get('get')
            if get is not None:
                setattr(cls, get, cls.__make_get(get, attr, container_type))

        if len(clsconf) == 1:
            setattr(cls, '__getitem__', cls.__make_getitem(attr, container_type))
