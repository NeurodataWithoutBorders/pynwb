from h5py import RegionReference
import numpy as np
import pandas as pd

from hdmf.utils import docval, getargs, ExtenderMeta, call_docval_func, popargs, get_docval
from hdmf import Container, Data, DataRegion, get_region_slicer
from hdmf.container import AbstractContainer
from hdmf.utils import LabelledDict
from hdmf.container import MultiContainerInterface as hdmf_MultiContainerInterface
from hdmf.common import DynamicTable, DynamicTableRegion  # noqa: F401
from hdmf.common import VectorData, VectorIndex, ElementIdentifiers  # noqa: F401

from . import CORE_NAMESPACE, register_class


def _not_parent(arg):
    return arg['name'] != 'parent'


def prepend_string(string, prepend='    '):
    return prepend + prepend.join(string.splitlines(True))


class NWBMixin(AbstractContainer):

    _data_type_attr = 'neurodata_type'

    @docval({'name': 'neurodata_type', 'type': str, 'doc': 'the data_type to search for', 'default': None})
    def get_ancestor(self, **kwargs):
        """
        Traverse parent hierarchy and return first instance of the specified data_type
        """
        neurodata_type = getargs('neurodata_type', kwargs)
        return super().get_ancestor(data_type=neurodata_type)


@register_class('NWBContainer', CORE_NAMESPACE)
class NWBContainer(NWBMixin, Container):

    _fieldsname = '__nwbfields__'

    __nwbfields__ = tuple()

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'})
    def __init__(self, **kwargs):
        call_docval_func(super(NWBContainer, self).__init__, kwargs)

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
class NWBData(NWBMixin, Data):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('array_data', 'data', Data), 'doc': 'the source of the data'})
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


@register_class('ScratchData', CORE_NAMESPACE)
class ScratchData(NWBData):

    __nwbfields__ = ('notes',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('array_data', 'data', Data), 'doc': 'the source of the data'},
            {'name': 'notes', 'type': str, 'doc': 'notes about the data', 'default': ''})
    def __init__(self, **kwargs):
        call_docval_func(super(ScratchData, self).__init__, kwargs)
        self.notes = getargs('notes', kwargs)


class NWBTable(NWBData):
    r'''
    Subclasses should specify the class attribute \_\_columns\_\_.

    This should be a list of dictionaries with the following keys:

    - ``name``            the column name
    - ``type``            the type of data in this column
    - ``doc``             a brief description of what gets stored in this column

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
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the source of the data', 'default': list()})
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


class MultiContainerInterface(NWBMixin, hdmf_MultiContainerInterface):
    pass
