from warnings import warn

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

    def _warn_on_new_pass_on_construct(self, warn_msg: str):
        """
        Issue a warning when a check is violated on instance creation.
        When reading from a file, do nothing, ensuring that files with
        deprecated neurodata types can be read without warnings.
        """
        if not self._in_construct_mode:
            warn(warn_msg)

    def _get_type_map(self):
        return get_type_map(copy=False)

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


@register_class('ScratchData', CORE_NAMESPACE)
class ScratchData(NWBData):

    __nwbfields__ = ('description', )

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this container'},
            {'name': 'data', 'type': ('scalar_data', 'array_data', 'data', Data), 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'notes about the data', 'default': None},
            allow_positional=AllowPositional.WARNING,)
    def __init__(self, **kwargs):
        description = popargs('description', kwargs)
        super().__init__(**kwargs)
        if not description:
            self._error_on_new_pass_on_construct(error_msg='ScratchData.description is required.')
        self.description = description


class NWBTable(Table):
    """Defined in PyNWB for API backward compatibility. See HDMF Table for details."""
    pass


class MultiContainerInterface(NWBDataInterface, hdmf_MultiContainerInterface):
    """Defined in PyNWB for API backward compatibility. See HDMF MultiContainterInterface for details."""

    pass
