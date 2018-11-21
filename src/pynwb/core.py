from h5py import RegionReference
import numpy as np
import pandas as pd

from .form.utils import docval, getargs, ExtenderMeta, call_docval_func, popargs, get_docval, fmt_docval_args, pystr
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

    def __repr__(self):
        template = "\n{} {}\nFields:\n""".format(getattr(self, 'name'), type(self))
        for k in sorted(self.fields):  # sorted to enable tests
            v = self.fields[k]
            template += "  {}: {}\n".format(k, self.__smart_str(v))
        return template

    @staticmethod
    def __smart_str(v):
        """
        Print compact string representation of data.

        If v is a list, try to print it using numpy. This will condense the string
        representation of datasets with many elements. If that doesn't work, just print the list.

        If v is a dictionary, print the name and type of each element

        If v is a neurodata_type, print the name of type

        Otherwise, use the built-in str()
        Parameters
        ----------
        v

        Returns
        -------
        str

        """
        if isinstance(v, list):
            try:
                return str(np.array(v))
            except ValueError:
                return str(v)
        elif isinstance(v, dict):
            template = '{'
            keys = list(sorted(v.keys()))
            for k in keys[:-1]:
                template += " {} {}, ".format(k, type(v[k]))
            if keys:
                template += " {} {}".format(keys[-1], type(v[keys[-1]]))
            return template + ' }'
        elif isinstance(v, NWBBaseType):
            "{} {}".format(getattr(v, 'name'), type(v))
        else:
            return str(v)


@register_class('NWBContainer', CORE_NAMESPACE)
class NWBContainer(NWBBaseType, Container):

    __nwbfields__ = ('help',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
             'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(NWBContainer, self).__init__, kwargs)

    __pconf_allowed_keys = {'name', 'child', 'required_name', 'doc'}

    @classmethod
    def _setter(cls, nwbfield):
        super_setter = NWBBaseType._setter(nwbfield)
        ret = [super_setter]
        if isinstance(nwbfield, dict):
            for k in nwbfield.keys():
                if k not in cls.__pconf_allowed_keys:
                    msg = "Unrecognized key '%s' in __nwbfield__ config '%s' on %s" %\
                           (k, nwbfield['name'], cls.__name__)
                    raise ValueError(msg)
            if nwbfield.get('required_name', None) is not None:
                name = nwbfield['required_name']
                idx1 = len(ret) - 1

                def nwbdi_setter(self, val):
                    if val is not None and val.name != name:
                        msg = "%s field on %s must be named '%s'" % (nwbfield['name'], self.__class__.__name__, name)
                        raise ValueError(msg)
                    ret[idx1](self, val)

                ret.append(nwbdi_setter)
            if nwbfield.get('child', False):
                idx2 = len(ret) - 1

                def nwbdi_setter(self, val):
                    ret[idx2](self, val)
                    if val is not None:
                        if isinstance(val, (tuple, list)):
                            pass
                        elif isinstance(val, dict):
                            val = val.values()
                        else:
                            val = [val]
                        for v in val:
                            self.add_child(v)

                ret.append(nwbdi_setter)
        return ret[-1]

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
        if isinstance(self.data, (tuple, list)) and isinstance(args, (tuple, list)):
            return [self.data[i] for i in args]
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


@register_class('Index', CORE_NAMESPACE)
class Index(NWBData):

    __nwbfields__ = ("target",)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors'},
            {'name': 'target', 'type': NWBData,
             'doc': 'the target dataset that this index applies to'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(Index, self).__init__, kwargs)


@register_class('VectorData', CORE_NAMESPACE)
class VectorData(NWBData):

    __nwbfields__ = ("description",)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData'},
            {'name': 'description', 'type': str, 'doc': 'a description for this column'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors', 'default': list()},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(VectorData, self).__init__, kwargs)
        self.description = getargs('description', kwargs)

    @docval({'name': 'val', 'type': None, 'doc': 'the value to add to this column'})
    def add_row(self, **kwargs):
        val = getargs('val', kwargs)
        self.data.append(val)


@register_class('VectorIndex', CORE_NAMESPACE)
class VectorIndex(Index):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorIndex'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a 1D dataset containing indexes that apply to VectorData object'},
            {'name': 'target', 'type': VectorData,
             'doc': 'the target dataset that this index applies to'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(VectorIndex, self).__init__, kwargs)
        self.target = getargs('target', kwargs)

    def add_vector(self, arg):
        self.target.extend(arg)
        self.data.append(len(self.target))

    def add_row(self, arg):
        self.target.extend(arg)
        self.data.append(len(self.target))

    def __getitem_helper(self, arg):
        start = 0 if arg == 0 else self.data[arg-1]
        end = self.data[arg]
        return self.target[start:end]

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            indices = list(range(*arg.indices(len(self.data))))
            ret = list()
            for i in indices:
                ret.append(self.__getitem_helper(i))
            return ret
        else:
            return self.__getitem_helper(arg)


@register_class('ElementIdentifiers', CORE_NAMESPACE)
class ElementIdentifiers(NWBData):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this ElementIdentifiers'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'a 1D dataset containing identifiers',
             'default': list()},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ElementIdentifiers, self).__init__, kwargs)


class NWBTable(NWBData):
    r'''
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
    '''  # noqa: W605

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

    def to_dataframe(self):
        '''Produce a pandas DataFrame containing this table's data.
        '''

        data = {colname: self[colname] for ii, colname in enumerate(self.columns)}
        return pd.DataFrame(data)

    @classmethod
    @docval(
        {'name': 'df', 'type': pd.DataFrame, 'doc': 'input data'},
        {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': None},
        {
            'name': 'extra_ok',
            'type': bool,
            'doc': 'accept (and ignore) unexpected columns on the input dataframe',
            'default': False
        },
    )
    def from_dataframe(cls, **kwargs):
        '''Construct an instance of NWBTable (or a subclass) from a pandas DataFrame. The columns of the dataframe
        should match the columns defined on the NWBTable subclass.
        '''

        df, name, extra_ok = getargs('df', 'name', 'extra_ok', kwargs)

        cls_cols = list([col['name'] for col in getattr(cls, '__columns__')])
        df_cols = list(df.columns)

        missing_columns = set(cls_cols) - set(df_cols)
        extra_columns = set(df_cols) - set(cls_cols)

        if extra_columns:
            raise ValueError(
                'unrecognized column(s) {} for table class {} (columns {})'.format(
                    extra_columns, cls.__name__, cls_cols
                )
            )

        use_index = False
        if len(missing_columns) == 1 and list(missing_columns)[0] == df.index.name:
            use_index = True

        elif missing_columns:
            raise ValueError(
                'missing column(s) {} for table class {} (columns {}, provided {})'.format(
                    missing_columns, cls.__name__, cls_cols, df_cols
                )
            )

        data = []
        for index, row in df.iterrows():
            if use_index:
                data.append([
                    row[colname] if colname != df.index.name else index
                    for colname in cls_cols
                ])
            else:
                data.append([row[colname] for colname in cls_cols])

        if name is None:
            return cls(data=data)
        return cls(name=name, data=data)


# diamond inheritance
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
        @docval({'name': attr_name, 'type': (list, tuple, dict, container_type),
                 'doc': '%s to store in this interface' % container_type.__name__, 'default': dict()},
                {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': cls.__name__},
                func_name='__init__')
        def _func(self, **kwargs):
            container = popargs(attr_name, kwargs)
            super(cls, self).__init__(**kwargs)
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

            # create the constructor, only if it has not been overridden
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


@register_class('DynamicTable', CORE_NAMESPACE)
class DynamicTable(NWBDataInterface):
    """
    A column-based table. Columns are defined by the argument *columns*. This argument
    must be a list/tuple of VectorDatas and VectorIndexes or a list/tuple of dicts containing the keys
    'name' and 'description' that provide the name and description of each column
    in the table. If specifying columns with a list/tuple of dicts, VectorData columns can
    be specified by setting the key 'index' to True.
    """

    __nwbfields__ = (
        {'name': 'id', 'child': True},
        {'name': 'columns', 'child': True},
        'colnames',
        'description'
    )

    __columns__ = tuple()

    @ExtenderMeta.pre_init
    def __gather_columns(cls, name, bases, classdict):
        '''
        This classmethod will be called during class declaration in the metaclass to automatically
        create setters and getters for NWB fields that need to be exported
        '''
        if not isinstance(cls.__columns__, tuple):
            msg = "'__columns__' must be of type tuple, found %s" % type(cls.__columns__)
            raise TypeError(msg)

        if len(bases) and 'DynamicTable' in globals() and issubclass(bases[-1], NWBContainer) \
           and bases[-1].__columns__ is not cls.__columns__:
                new_columns = list(cls.__columns__)
                new_columns[0:0] = bases[-1].__columns__
                cls.__columns__ = tuple(new_columns)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this table'},    # noqa: C901
            {'name': 'description', 'type': str, 'doc': 'a description of what is in this table'},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers), 'doc': 'the identifiers for this table',
             'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
             'default': None})
    def __init__(self, **kwargs):
        id, columns, desc, colnames = popargs('id', 'columns', 'description', 'colnames', kwargs)
        call_docval_func(super(DynamicTable, self).__init__, kwargs)
        self.description = desc

        if id is not None:
            if not isinstance(id, ElementIdentifiers):
                id = ElementIdentifiers('id', data=id)
        else:
            id = ElementIdentifiers('id')

        if columns is not None:
            if len(columns) > 0:
                if isinstance(columns[0], dict):
                    columns = self.__build_columns(columns)
                elif not all(isinstance(c, (VectorData, VectorIndex)) for c in columns):
                    raise ValueError("'columns' must be a list of VectorData, DynamicTableRegion or VectorIndex")
                colset = {c.name: c for c in columns}
                for c in columns:
                    if isinstance(c, VectorIndex):
                        colset.pop(c.target.name)
                lens = [len(c) for c in colset.values()]
                if not all(i == lens[0] for i in lens):
                    raise ValueError("columns must be the same length")
                if lens[0] != len(id):
                    if len(id) > 0:
                        raise ValueError("must provide same number of ids as length of columns")
                    else:
                        id.data.extend(range(lens[0]))
        else:
            columns = list()

        self.id = id

        if colnames is None:
            if columns is None:
                self.colnames = list()
                self.columns = list()
            else:
                tmp = list()
                for col in columns:
                    if isinstance(col, VectorIndex):
                        continue
                    tmp.append(col.name)
                self.colnames = tuple(tmp)
                self.columns = columns
        else:
            if columns is None:
                raise ValueError("Must supply 'columns' if specifying 'colnames'")
            else:
                # make sure columns order matches colnames order
                self.colnames = tuple(pystr(c) for c in colnames)
                col_dict = {col.name: col for col in columns}
                order = dict()
                indexed = dict()
                for col in columns:
                    if isinstance(col, VectorIndex):
                        indexed[col.target.name] = True
                    else:
                        if col.name in indexed:
                            continue
                        indexed[col.name] = False
                i = 0
                for name in self.colnames:
                    col = col_dict[name]
                    order[col.name] = i
                    if indexed[col.name]:
                        i = i + 1
                    i = i + 1
                tmp = [None] * i
                for col in columns:
                    if indexed.get(col.name, False):
                        continue
                    if isinstance(col, VectorData):
                        pos = order[col.name]
                        tmp[pos] = col
                    elif isinstance(col, VectorIndex):
                        pos = order[col.target.name]
                        tmp[pos] = col
                        tmp[pos+1] = col.target
                self.columns = list(tmp)

        # to make generating DataFrames and Series easier
        col_dict = dict()
        for col in self.columns:
            if isinstance(col, VectorData):
                existing = col_dict.get(col.name)
                # if we added this column using its index, ignore this column
                if existing is not None:
                    if isinstance(existing, VectorIndex):
                        if existing.target.name == col.name:
                            continue
                        else:
                            raise ValueError("duplicate column does not target VectorData '%s'" % col.name)
                    else:
                        raise ValueError("duplicate column found: '%s'" % col.name)
                else:
                    col_dict[col.name] = col
            elif isinstance(col, VectorIndex):
                col_dict[col.target.name] = col  # use target name for reference and VectorIndex for retrieval

        self.__df_cols = [self.id] + [col_dict[name] for name in self.colnames]
        self.__colids = {name: i+1 for i, name in enumerate(self.colnames)}
        for col in self.__columns__:
            if col.get('required', False) and col['name'] not in self.__colids:
                self.add_column(col['name'], col['description'],
                                index=col.get('index', False),
                                table=col.get('table', False))

    @staticmethod
    def __build_columns(columns, df=None):
        tmp = list()
        for d in columns:
            name = d['name']
            desc = d.get('description', 'no description')
            data = None
            if df is not None:
                data = list(df[name].values)
            if d.get('index', False):
                index_data = None
                if data is not None:
                    index_data = [len(data[0])]
                    for i in range(1, len(data)):
                        index_data.append(len(data[i]) + index_data[i-1])
                    # assume data came in through a DataFrame, so we need
                    # to concatenate it
                    tmp_data = list()
                    for d in data:
                        tmp_data.extend(d)
                    data = tmp_data
                vdata = VectorData(name, desc, data=data)
                vindex = VectorIndex("%s_index" % name, index_data, target=vdata)
                tmp.append(vindex)
                tmp.append(vdata)
            else:
                if data is None:
                    data = list()
                cls = VectorData
                if d.get('table', False):
                    cls = DynamicTableRegion
                tmp.append(cls(name, desc, data=data))
        return tmp

    def __len__(self):
        return len(self.id)

    @docval({'name': 'data', 'type': dict, 'help': 'the data to put in this row', 'default': None},
            {'name': 'id', 'type': int, 'help': 'the ID for the row', 'default': None},
            allow_extra=True)
    def add_row(self, **kwargs):
        '''
        Add a row to the table. If *id* is not provided, it will auto-increment.
        '''
        data, row_id = popargs('data', 'id', kwargs)
        data = data if data is not None else kwargs

        extra_columns = set(list(data.keys())) - set(list(self.__colids.keys()))
        missing_columns = set(list(self.__colids.keys())) - set(list(data.keys()))

        # check to see if any of the extra columns just need to be added
        if extra_columns:
            for col in self.__columns__:
                if col['name'] in extra_columns:
                    if data[col['name']] is not None:
                        self.add_column(col['name'], col['description'],
                                        index=col.get('index', False),
                                        table=col.get('table', False))
                    extra_columns.remove(col['name'])

        if extra_columns or missing_columns:
            raise ValueError(
                '\n'.join([
                    'row data keys don\'t match available columns',
                    'you supplied {} extra keys: {}'.format(len(extra_columns), extra_columns),
                    'and were missing {} keys: {}'.format(len(missing_columns), missing_columns)
                ])
            )

        if row_id is None:
            row_id = data.pop('id', None)
        if row_id is None:
            row_id = len(self)
        self.id.data.append(row_id)

        for colname, colnum in self.__colids.items():
            if colname not in data:
                raise ValueError("column '%s' missing" % colname)
            c = self.__df_cols[colnum]
            if isinstance(c, VectorIndex):
                c.add_vector(data[colname])
            else:
                c.add_row(data[colname])

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData'},
            {'name': 'description', 'type': str, 'doc': 'a description for this column'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors', 'default': list()},
            {'name': 'table', 'type': (bool, 'DynamicTable'),
             'doc': 'whether or not this is a table region or the table the region applies to', 'default': False},
            {'name': 'index', 'type': (bool, VectorIndex, 'array_data'),
             'doc': 'whether or not this column should be indexed', 'default': False})
    def add_column(self, **kwargs):
        """
        Add a column to this table. If data is provided, it must
        contain the same number of rows as the current state of the table.
        """
        name, data = getargs('name', 'data', kwargs)
        index, table = popargs('index', 'table', kwargs)
        if name in self.__colids:
            msg = "column '%s' already exists in DynamicTable '%s'" % (name, self.name)
            raise ValueError(msg)

        ckwargs = dict(kwargs)
        cls = VectorData

        # Add table if it's been specified
        if table is not False:
            cls = DynamicTableRegion
            if isinstance(table, DynamicTable):
                ckwargs['table'] = table

        col = cls(**ckwargs)
        self.add_child(col)
        columns = [col]

        # Add index if it's been specified
        if index is not False:
            if isinstance(index, VectorIndex):
                col_index = index
            elif isinstance(index, bool):        # make empty VectorIndex
                if len(col) > 0:
                    raise ValueError("cannot pass empty index with non-empty data to index")
                col_index = VectorIndex(name + "_index", list(), col)
            else:                                # make VectorIndex with supplied data
                if len(col) == 0:
                    raise ValueError("cannot pass non-empty index with empty data to index")
                col_index = VectorIndex(name + "_index", index, col)
            columns.insert(0, col_index)
            self.add_child(col_index)
            col = col_index

        if len(col) != len(self.id):
            raise ValueError("column must have the same number of rows as 'id'")
        self.__colids[name] = len(self.__df_cols)
        self.fields['colnames'] = tuple(list(self.colnames)+[name])
        self.fields['columns'] = tuple(list(self.columns)+columns)
        self.__df_cols.append(col)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the DynamicTableRegion object'},
            {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what the region is'})
    def create_region(self, **kwargs):
        region = getargs('region', kwargs)
        if isinstance(region, slice):
            if (region.start is not None and region.start < 0) or (region.stop is not None and region.stop > len(self)):
                msg = 'region slice %s is out of range for this DynamicTable of length ' % (str(region), len(self))
                raise IndexError(msg)
            region = list(range(*region.indices(len(self))))
        else:
            for idx in region:
                if idx < 0 or idx >= len(self):
                    raise IndexError('The index ' + str(idx) +
                                     ' is out of range for this DynamicTable of length '
                                     + str(len(self)))
        desc = getargs('description', kwargs)
        name = getargs('name', kwargs)
        return DynamicTableRegion(name, region, desc, self)

    def __getitem__(self, key):
        ret = None
        if isinstance(key, tuple):
            # index by row and column, return specific cell
            arg1 = key[0]
            arg2 = key[1]
            if isinstance(arg2, str):
                arg2 = self.__colids[arg2]
            ret = self.__df_cols[arg2][arg1]
        else:
            arg = key
            if isinstance(arg, str):
                # index by one string, return column
                ret = self.__df_cols[self.__colids[arg]]
            elif isinstance(arg, (int, np.int8, np.int16, np.int32, np.int64)):
                # index by int, return row
                ret = tuple(col[arg] for col in self.__df_cols)
            elif isinstance(arg, (tuple, list)):
                # index by a list of ints, return multiple rows
                ret = list()
                for i in arg:
                    ret.append(tuple(col[i] for col in self.__df_cols))

        return ret

    def __contains__(self, val):
        return val in self.__colids

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def to_dataframe(self):
        '''Produce a pandas DataFrame containing this table's data.
        '''

        data = {}
        for name in self.colnames:
            col = self.__df_cols[self.__colids[name]]
            data[name] = col[:]

        return pd.DataFrame(data, index=pd.Index(name=self.id.name, data=self.id.data))

    @classmethod
    @docval(
        {'name': 'df', 'type': pd.DataFrame, 'doc': 'source DataFrame'},
        {'name': 'name', 'type': str, 'doc': 'the name of this table'},
        {
            'name': 'index_column',
            'type': str,
            'help': 'if provided, this column will become the table\'s index',
            'default': None
        },
        {
            'name': 'table_description',
            'type': str,
            'help': 'a description of what is in the resulting table',
            'default': ''
        },
        {
            'name': 'columns',
            'type': (list, tuple),
            'help': 'a list/tuple of dictionaries specifying columns in the table',
            'default': None
        },
        allow_extra=True
    )
    def from_dataframe(cls, **kwargs):
        '''Construct an instance of DynamicTable (or a subclass) from a pandas DataFrame. The columns of the resulting
        table are defined by the columns of the dataframe and the index by the dataframe's index (make sure it has a
        name!) or by a column whose name is supplied to the index_column parameter. We recommend that you supply
        *columns* - a list/tuple of dictionaries containing the name and description of the column- to help others
        understand the contents of your table. See :py:class:`~pynwb.core.DynamicTable` for more details on *columns*.
        '''

        df = kwargs.pop('df')
        name = kwargs.pop('name')
        index_column = kwargs.pop('index_column')
        table_description = kwargs.pop('table_description')
        columns = kwargs.pop('columns')

        if columns is None:
            columns = [{'name': s} for s in df.columns]
        else:
            columns = list(columns)
            existing = set(c['name'] for c in columns)
            for c in df.columns:
                if c not in existing:
                    columns.append({'name': c})

        if index_column is not None:
            ids = ElementIdentifiers(name=index_column, data=df[index_column].values.tolist())
        else:
            index_name = df.index.name if df.index.name is not None else 'id'
            ids = ElementIdentifiers(name=index_name, data=df.index.values.tolist())

        columns = cls.__build_columns(columns, df=df)

        return cls(name=name, id=ids, columns=columns, description=table_description, **kwargs)


@register_class('DynamicTableRegion', CORE_NAMESPACE)
class DynamicTableRegion(VectorData):
    """
    An object for easily slicing into a DynamicTable
    """

    __nwbfields__ = (
        'table',
        'description'
    )

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this VectorData'},
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors'},
            {'name': 'description', 'type': str, 'doc': 'a description of what this region represents'},
            {'name': 'table', 'type': DynamicTable,
             'doc': 'the DynamicTable this region applies to', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        t = popargs('table', kwargs)
        call_docval_func(super(DynamicTableRegion, self).__init__, kwargs)
        self.table = t

    @property
    def table(self):
        return self.fields.get('table')

    @table.setter
    def table(self, val):
        if val is None:
            return
        if 'table' in self.fields:
            msg = "can't set attribute 'table' -- already set"
            raise AttributeError(msg)
        for idx in self.data:
            if idx < 0 or idx >= len(val):
                raise IndexError('The index ' + str(idx) +
                                 ' is out of range for this DynamicTable of length '
                                 + str(len(val)))
        self.fields['table'] = val

    def __getitem__(self, key):
        # treat the list of indices as data that can be indexed. then pass the
        # result to the table to get the data
        if isinstance(key, tuple):
            arg1 = key[0]
            arg2 = key[1]
            return self.table[self.data[arg1], arg2]
        else:
            if isinstance(key, int):
                return self.table[self.data[key]]
            else:
                raise ValueError("unrecognized argument: '%s'" % key)
