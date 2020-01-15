from hdmf.utils import docval, call_docval_func
from . import register_class, CORE_NAMESPACE
from .core import NWBContainer


@register_class('Device', CORE_NAMESPACE)
class Device(NWBContainer):
    """
    """

    __nwbfields__ = ('name',
                     'description',
                     'manufacturer')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this device'},
            {'name': 'description', 'type': str,
             'doc': 'Description of the device (e.g., model, firmware version, processing software version, etc.)',
             'default': None},
            {'name': 'manufacturer', 'type': str, 'doc': 'the name of the manufacturer of this device',
            'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(Device, self).__init__, kwargs)
