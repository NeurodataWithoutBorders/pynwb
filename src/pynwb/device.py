from hdmf.utils import docval, popargs

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer


@register_class('Device', CORE_NAMESPACE)
class Device(NWBContainer):
    """
    Metadata about a data acquisition device, e.g., recording system, electrode, microscope.
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
        description, manufacturer = popargs('description', 'manufacturer', kwargs)
        super().__init__(**kwargs)
        self.description = description
        self.manufacturer = manufacturer
