from warnings import warn

import numpy as np

from hdmf import Container, Data
from hdmf.container import AbstractContainer, MultiContainerInterface as hdmf_MultiContainerInterface, Table
from hdmf.common import DynamicTable, DynamicTableRegion  # noqa: F401
from hdmf.common import VectorData, VectorIndex, ElementIdentifiers  # noqa: F401
from hdmf.utils import docval, popargs, AllowPositional
from hdmf.utils import LabelledDict  # noqa: F401

from . import CORE_NAMESPACE, register_class
from pynwb import get_type_map


__all__ = [
    'NWBMixin',
    'NWBContainer',
    'NWBDataInterface',
    'NWBData',
    'ScratchData',
    'NWBTable',
    'MultiContainerInterface'
]


class NWBMixin(AbstractContainer):

    _data_type_attr = 'neurodata_type'

    _fieldsname = '__nwbfields__'

    __nwbfields__ = tuple()

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
        files with invalid data can be read.
        """
        if not self._in_construct_mode:
            raise ValueError(error_msg)
        warn(error_msg)

    def _error_on_new_pass_on_construct(self, error_msg: str):
        """
        Raise an error when a check is violated on instance creation.
        When reading from a file, do nothing, ensuring that files with
        invalid data or deprecated neurodata types can be read.
        """
        if not self._in_construct_mode:
            raise ValueError(error_msg)

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

    pass


@register_class('NWBDataInterface', CORE_NAMESPACE)
class NWBDataInterface(NWBContainer):

    pass


@register_class('NWBData', CORE_NAMESPACE)
class NWBData(NWBMixin, Data):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('scalar_data', 'array_data', 'data', Data), 'doc': 'the source of the data'},
            allow_positional=AllowPositional.WARNING,)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__data = kwargs['data']

    @property
    def data(self):
        """The data managed by this object"""
        return self.__data

    def __len__(self):
        """Size of the data. Same as len(self.data)"""
        return len(self.__data)

    def __getitem__(self, args):
        if isinstance(self.data, (tuple, list)) and isinstance(args, (tuple, list)):
            return [self.data[i] for i in args]
        return self.data[args]

    def append(self, arg):
        """
        Append a single element to the data

        Note: The arg to append should be 1 dimension less than the data.
        For example, if the data is a 2D array, arg should be a 1D array.
        Appending to scalar data is not supported. To append multiple
        elements, use extend.
        """
        if isinstance(self.data, list):
            self.data.append(arg)
        elif isinstance(self.data, np.ndarray):
            self.__data = np.concatenate((self.__data, [arg]))
        else:
            msg = "NWBData cannot append to object of type '%s'" % type(self.__data)
            raise ValueError(msg)

    def extend(self, arg):
        """
        Extend the data with multiple elements.
        """
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
             'doc': 'notes about the data. This argument will be deprecated. Use description instead', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'notes about the data', 'default': None},
            allow_positional=AllowPositional.WARNING,)
    def __init__(self, **kwargs):
        notes, description = popargs('notes', 'description', kwargs)
        super().__init__(**kwargs)
        if notes is not None:
            self._error_on_new_pass_on_construct(
                    error_msg=("The `notes` argument of ScratchData.__init__ has been deprecated and "
                               "will be removed in PyNWB 4.0. Use description instead.")
                    )
            if notes is not None and description is not None:
                raise ValueError('Cannot provide both notes and description to ScratchData.__init__. The description '
                                 'argument is recommended.')
            description = notes
        if not description:
            self._error_on_new_pass_on_construct(error_msg='ScratchData.description is required.')
        self.description = description

    @property
    def notes(self):
        """
        Get the notes attribute. Use of ScratchData.notes has been deprecated and will be removed in PyNWB 4.0.
        """
        warn(("Use of ScratchData.notes has been deprecated and will be removed in PyNWB 4.0. "
              "Use ScratchData.description instead."), DeprecationWarning)
        return self.description

    @notes.setter
    def notes(self, value):
        """
        Set the notes attribute. Use of ScratchData.notes has been deprecated and will be removed in PyNWB 4.0.
        """
        self._error_on_new_pass_on_construct(
                    error_msg=("Use of ScratchData.notes has been deprecated and will be removed in PyNWB 4.0. "
                               "Use ScratchData.description instead."))
        self.description = value


class NWBTable(Table):
    """Defined in PyNWB for API backward compatibility. See HDMF Table for details."""
    pass


class MultiContainerInterface(NWBDataInterface, hdmf_MultiContainerInterface):
    """Defined in PyNWB for API backward compatibility. See HDMF MultiContainterInterface for details."""

    pass
