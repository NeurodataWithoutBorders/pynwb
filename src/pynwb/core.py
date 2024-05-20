from warnings import warn

import numpy as np

from hdmf import Container, Data
from hdmf.container import AbstractContainer, MultiContainerInterface as hdmf_MultiContainerInterface, Table
from hdmf.common import DynamicTable, DynamicTableRegion  # noqa: F401
from hdmf.common import VectorData, VectorIndex, ElementIdentifiers  # noqa: F401
from hdmf.utils import docval, popargs
from hdmf.utils import LabelledDict  # noqa: F401

from . import CORE_NAMESPACE, register_class
from pynwb import get_type_map


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
        neurodata_type = kwargs['neurodata_type']
        return super().get_ancestor(data_type=neurodata_type)

    def _error_on_new_warn_on_construct(self, error_msg: str):
        """
        Raise an error when a check is violated on instance creation.
        To ensure backwards compatibility, this method throws a warning
        instead of raising an error when reading from a file, ensuring that
        files with invalid data can be read. If error_msg is set to None
        the function will simply return without further action.
        """
        if error_msg is None:
            return
        if not self._in_construct_mode:
            raise ValueError(error_msg)
        warn(error_msg)

    def _get_type_map(self):
        return get_type_map()

    @property
    def data_type(self):
        """
        Return the spec data type associated with this container, i.e., the neurodata_type.
        """
        # we need this function here to use the correct _data_type_attr.
        _type = getattr(self, self._data_type_attr)
        return _type


@register_class('NWBContainer', CORE_NAMESPACE)
class NWBContainer(NWBMixin, Container):

    _fieldsname = '__nwbfields__'

    __nwbfields__ = tuple()


@register_class('NWBDataInterface', CORE_NAMESPACE)
class NWBDataInterface(NWBContainer):

    pass


@register_class('NWBData', CORE_NAMESPACE)
class NWBData(NWBMixin, Data):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('scalar_data', 'array_data', 'data', Data), 'doc': 'the source of the data'})
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__data = kwargs['data']

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
            self.__data = np.concatenate((self.__data, [arg]))
        else:
            msg = "NWBData cannot append to object of type '%s'" % type(self.__data)
            raise ValueError(msg)

    def extend(self, arg):
        if isinstance(self.data, list):
            self.data.extend(arg)
        elif isinstance(self.data, np.ndarray):
            self.__data = np.concatenate((self.__data, arg))
        else:
            msg = "NWBData cannot extend object of type '%s'" % type(self.__data)
            raise ValueError(msg)


@register_class('ScratchData', CORE_NAMESPACE)
class ScratchData(NWBData):

    __nwbfields__ = ('description', )

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('scalar_data', 'array_data', 'data', Data), 'doc': 'the source of the data'},
            {'name': 'notes', 'type': str,
             'doc': 'notes about the data. This argument will be deprecated. Use description instead', 'default': ''},
            {'name': 'description', 'type': str, 'doc': 'notes about the data', 'default': None})
    def __init__(self, **kwargs):
        notes, description = popargs('notes', 'description', kwargs)
        super().__init__(**kwargs)
        if notes != '':
            warn('The `notes` argument of ScratchData.__init__ will be deprecated. Use description instead.',
                 PendingDeprecationWarning)
            if notes != '' and description != '':
                raise ValueError('Cannot provide both notes and description to ScratchData.__init__. The description '
                                 'argument is recommended.')
            description = notes
        if not description:
            warn('ScratchData.description will be required in a future major release of PyNWB.',
                 PendingDeprecationWarning)
        self.description = description

    @property
    def notes(self):
        warn('Use of ScratchData.notes will be deprecated. Use ScratchData.description instead.',
             PendingDeprecationWarning)
        return self.description

    @notes.setter
    def notes(self, value):
        warn('Use of ScratchData.notes will be deprecated. Use ScratchData.description instead.',
             PendingDeprecationWarning)
        self.description = value


class NWBTable(Table):
    """Defined in PyNWB for API backward compatibility. See HDMF Table for details."""
    pass


class MultiContainerInterface(NWBDataInterface, hdmf_MultiContainerInterface):
    """Defined in PyNWB for API backward compatibility. See HDMF MultiContainterInterface for details."""

    pass
