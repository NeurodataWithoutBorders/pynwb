from collections import Iterable
from warnings import warn

import numpy as np
import pandas as pd

from . import register_class, CORE_NAMESPACE

from .core import NWBDataInterface, MultiContainerInterface, NWBContainer, NWBData
from .form.data_utils import AbstractDataChunkIterator, DataIO
from .form.utils import docval, getargs, ExtenderMeta, call_docval_func, popargs, get_docval, fmt_docval_args, pystr


_default_conversion = 1.0
_default_resolution = 0.0


@register_class('ProcessingModule', CORE_NAMESPACE)
class ProcessingModule(MultiContainerInterface):
    """ Processing module. This is a container for one or more containers
        that provide data at intermediate levels of analysis

        ProcessingModules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """

    __nwbfields__ = ('description',)

    __clsconf__ = {
            'attr': 'data_interfaces',
            'add': 'add_data_interface',
            'type': NWBDataInterface,
            'get': 'get_data_interface'
    }

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this processing module'},
            {'name': 'description', 'type': str, 'doc': 'Description of this processing module'},
            {'name': 'data_interfaces', 'type': (list, tuple, dict),
             'doc': 'NWBDataInterfacess that belong to this ProcessingModule', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ProcessingModule, self).__init__, kwargs)
        self.description = popargs('description', kwargs)
        self.data_interfaces = popargs('data_interfaces', kwargs)

    @property
    def containers(self):
        return self.data_interfaces

    def __getitem__(self, arg):
        return self.get_data_interface(arg)

    @docval({'name': 'container', 'type': NWBDataInterface, 'doc': 'the NWBDataInterface to add to this Module'})
    def add_container(self, **kwargs):
        '''
        Add an NWBContainer to this ProcessingModule
        '''
        container = getargs('container', kwargs)
        warn(PendingDeprecationWarning('add_container will be replaced by add_data_interface'))
        self.add_data_interface(container)

    @docval({'name': 'container_name', 'type': str, 'doc': 'the name of the NWBContainer to retrieve'})
    def get_container(self, **kwargs):
        '''
        Retrieve an NWBContainer from this ProcessingModule
        '''
        container_name = getargs('container_name', kwargs)
        warn(PendingDeprecationWarning('get_container will be replaced by get_data_interface'))
        return self.get_data_interface(container_name)


@register_class('TimeSeries', CORE_NAMESPACE)
class TimeSeries(NWBDataInterface):
    """A generic base class for time series data"""
    __nwbfields__ = ("comments",
                     "description",
                     "data",
                     "resolution",
                     "conversion",
                     "unit",
                     "num_samples",
                     "timestamps",
                     "timestamps_unit",
                     "interval",
                     "starting_time",
                     "rate",
                     "starting_time_unit",
                     "control",
                     "control_description")

    __time_unit = "Seconds"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'resolution', 'type': (str, float),
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            # Optional arguments:
            {'name': 'conversion', 'type': (str, float),
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},

            {'name': 'timestamps', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        """Create a TimeSeries object
        """
        pargs, pkwargs = fmt_docval_args(super(TimeSeries, self).__init__, kwargs)
        super(TimeSeries, self).__init__(*pargs, **pkwargs)
        keys = ("resolution",
                "comments",
                "description",
                "conversion",
                "unit",
                "control",
                "control_description")
        for key in keys:
            val = kwargs.get(key)
            if val is not None:
                setattr(self, key, val)

        data = getargs('data', kwargs)
        self.fields['data'] = data
        if isinstance(data, TimeSeries):
            data.__add_link('data_link', self)
            self.fields['num_samples'] = data.num_samples
        elif isinstance(data, AbstractDataChunkIterator):
            self.fields['num_samples'] = -1
        elif isinstance(data, DataIO):
            this_data = data.data
            if isinstance(this_data, AbstractDataChunkIterator):
                self.fields['num_samples'] = -1
            else:
                self.fields['num_samples'] = len(this_data)
        elif data is None:
            self.fields['num_samples'] = 0
        else:
            self.fields['num_samples'] = len(data)

        timestamps = kwargs.get('timestamps')
        starting_time = kwargs.get('starting_time')
        rate = kwargs.get('rate')
        if timestamps is not None:
            if rate is not None:
                raise ValueError('Specifying rate and timestamps is not supported.')
            if starting_time is not None:
                raise ValueError('Specifying starting_time and timestamps is not supported.')
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = 'Seconds'
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.__add_link('timestamp_link', self)
        elif rate is not None:
            self.rate = rate
            if starting_time is not None:
                self.starting_time = starting_time
                self.starting_time_unit = 'Seconds'
            else:
                self.starting_time = 0.0
        else:
            raise TypeError("either 'timestamps' or 'rate' must be specified")

    @property
    def data(self):
        if isinstance(self.fields['data'], TimeSeries):
            return self.fields['data'].data
        else:
            return self.fields['data']

    @property
    def data_link(self):
        return self.__get_links('data_link')

    @property
    def timestamps(self):
        if 'timestamps' not in self.fields:
            return None
        if isinstance(self.fields['timestamps'], TimeSeries):
            return self.fields['timestamps'].timestamps
        else:
            return self.fields['timestamps']

    @property
    def timestamp_link(self):
        return self.__get_links('timestamp_link')

    def __get_links(self, links):
        ret = self.fields.get(links, list())
        if ret is not None:
            ret = set(ret)
        return ret

    def __add_link(self, links_key, link):
        self.fields.setdefault(links_key, list()).append(link)

    @property
    def time_unit(self):
        return self.__time_unit


@register_class('Image', CORE_NAMESPACE)
class Image(NWBData):
    __nwbfields__ = ('data', 'resolution', 'description')

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image',
             'shape': ((None, None), (None, None, 3), (None, None, 4))},
            {'name': 'resolution', 'type': float, 'doc': 'pixels / cm', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'description of image', 'default': None})
    def __init__(self, **kwargs):
        super(Image, self).__init__(name=kwargs['name'], data=kwargs['data'])
        self.resolution = kwargs['resolution']
        self.description = kwargs['description']


@register_class('Images', CORE_NAMESPACE)
class Images(NWBDataInterface):

    __clsconf__ = {
        'attr': 'images',
        'add': 'add_image',
        'type': Image,
        'get': 'get_image'
    }

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'images', 'type': (list, tuple, dict), 'doc': 'images'},
            {'name': 'description', 'type': str, 'doc': 'description of image', 'default': None})
    def __init__(self, **kwargs):
        super(Images, self).__init__(name=kwargs['name'])
        self.description = popargs('description', kwargs)


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
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'a dataset where the first dimension is a concatenation of multiple vectors'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'a description for this column', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(VectorData, self).__init__, kwargs)
        self.description = getargs('description', kwargs)


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


@register_class('TableColumn', CORE_NAMESPACE)
class TableColumn(NWBData):

    __nwbfields__ = (
        'description',
    )

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this column'},
            {'name': 'description', 'type': str, 'doc': 'a description for this column', 'default': None},
            {'name': 'data', 'type': 'array_data', 'doc': 'the data contained in this  column', 'default': list()})
    def __init__(self, **kwargs):
        desc = popargs('description', kwargs)
        call_docval_func(super(TableColumn, self).__init__, kwargs)
        self.description = desc

    @docval({'name': 'val', 'type': None, 'doc': 'the value to add to this column'})
    def add_row(self, **kwargs):
        val = getargs('val', kwargs)
        self.data.append(val)


@register_class('DynamicTable', CORE_NAMESPACE)
class DynamicTable(NWBDataInterface):
    """
    A column-based table. Columns are defined by the argument *columns*. This argument
    must be a list/tuple of TableColumns and VectorIndexes or a list/tuple of dicts containing the keys
    'name' and 'description' that provide the name and description of each column
    in the table. If specifying columns with a list/tuple of dicts, VectorData columns can
    be specified by setting the key 'vector_data' to True.
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
                elif not all(isinstance(c, (VectorData, VectorIndex, TableColumn)) for c in columns):
                    raise ValueError("'columns' must be a list of TableColumns, VectorData, or VectorIndex")
                lens = [len(c) for c in columns if isinstance(c, (TableColumn, VectorIndex))]
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
                i = 0
                for name in self.colnames:
                    col = col_dict[name]
                    order[col.name] = i
                    if isinstance(col, VectorData):
                        i = i + 1
                    i = i + 1
                tmp = [None] * i
                for col in columns:
                    if isinstance(col, TableColumn):
                        pos = order[col.name]
                        tmp[pos] = col
                    elif isinstance(col, VectorData):
                        continue
                    elif isinstance(col, VectorIndex):
                        pos = order[col.target.name]
                        tmp[pos] = col
                        tmp[pos+1] = col.target
                self.columns = list(tmp)

        # to make generating DataFrames and Series easier
        col_dict = dict()
        for col in self.columns:
            if isinstance(col, TableColumn):
                col_dict[col.name] = col
            elif isinstance(col, VectorIndex):
                col_dict[col.target.name] = col  # use target name for reference and VectorIndex for retrieval

        self.__df_cols = [self.id] + [col_dict[name] for name in self.colnames]
        self.__colids = {name: i+1 for i, name in enumerate(self.colnames)}
        for col in self.__columns__:
            if col.get('required', False) and col['name'] not in self.__colids:
                if not col.get('vector_data', False):
                    self.add_column(col['name'], col['description'])
                else:
                    self.add_vector_column(col['name'], col['description'])

    @staticmethod
    def __build_columns(columns, df=None):
        tmp = list()
        for d in columns:
            name = d['name']
            desc = d.get('description', 'no description')
            data = None
            if df is not None:
                data = list(df[name].values)
            if d.get('vector_data', False):
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
                vdata = VectorData(name, data, description=desc)
                vindex = VectorIndex("%s_index" % name, index_data, target=vdata)
                tmp.append(vindex)
                tmp.append(vdata)
            else:
                if data is None:
                    data = list()
                tmp.append(TableColumn(name, desc, data=data))
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
                        if not col.get('vector_data', False):
                            self.add_column(col['name'], col['description'])
                        else:
                            self.add_vector_column(col['name'], col['description'])
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

    @docval(*get_docval(TableColumn.__init__))
    def add_column(self, **kwargs):
        """
        Add a column to this table. If data is provided, it must
        contain the same number of rows as the current state of the table.
        """
        name, data = getargs('name', 'data', kwargs)
        if name in self.__colids:
            msg = "column '%s' already exists in DynamicTable '%s'" % (name, self.name)
            raise ValueError(msg)
        col = TableColumn(**kwargs)
        self.add_child(col)
        if len(data) != len(self.id):
            raise ValueError("column must have the same number of rows as 'id'")
        self.__colids[name] = len(self.__df_cols)
        self.fields['colnames'] = tuple(list(self.colnames)+[name])
        self.fields['columns'] = tuple(list(self.columns)+[col])
        self.__df_cols.append(col)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this vector column', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'a description for this vector column', 'default': None},
            {'name': 'index', 'type': 'array_data', 'doc': 'the index for this vector column', 'default': None},
            {'name': 'data', 'type': 'array_data', 'doc': 'the data contained in this vector column', 'default': None})
    def add_vector_column(self, **kwargs):
        """
        Add a column comprised of vector data (i.e. where the cells of
        the column are vectors rather than scalars) to this table

        If *name* and *description* are given, the index will be named *<name>_index*
        """
        index, data, name, description = getargs('index', 'data', 'name', 'description', kwargs)
        if index is None and data is None:
            if name is not None and description is not None:
                data = VectorData(name, list(), description=description)
                index = VectorIndex(name + "_index", list(), data)
            else:
                raise ValueError("Must supply 'index' and 'data' or 'name' and 'description'")
        elif index is not None and data is not None:
            if not isinstance(index, VectorIndex) and not isinstance(data, VectorData):
                pass
            else:
                if name is not None and description is not None:
                    data = VectorData(name, data, description=description)
                    index = VectorIndex(name + "_index", index, data)
                else:
                    msg = ("Must supply 'name' and 'description' if 'index' and 'data' ",
                           "are not VectorIndex and VectorData, respectively")
                    raise ValueError(msg)
        else:
            raise ValueError("Must supply both 'index' and 'data' or neither")
        self.add_child(index)
        self.add_child(data)
        if len(index) != len(self.id):
            raise ValueError("'index' must have the same number of rows as 'id'")
        self.__colids[name] = len(self.__df_cols)
        self.fields['colnames'] = tuple(list(self.colnames)+[name])
        self.fields['columns'] = tuple(list(self.columns)+[index, data])
        self.__df_cols.append(index)

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
                                     + str(len(self.electrodes)))
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
class DynamicTableRegion(NWBData):
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
             'doc': 'the DynamicTable this region applies to'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        t, d = popargs('table', 'description', kwargs)
        call_docval_func(super(DynamicTableRegion, self).__init__, kwargs)
        self.table = t
        self.description = d

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
