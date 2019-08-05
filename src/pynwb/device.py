from hdmf.utils import docval, call_docval_func
from . import register_class, CORE_NAMESPACE
from .core import NWBContainer


@register_class('Device', CORE_NAMESPACE)
class Device(NWBContainer):
    """
    """

    __nwbfields__ = ('name',)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this device'})
    def __init__(self, **kwargs):
        call_docval_func(super(Device, self).__init__, kwargs)
