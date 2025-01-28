from hdmf.utils import docval, popargs

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer


@register_class('Device', CORE_NAMESPACE)
class Device(NWBContainer):
    """
    Metadata about a data acquisition device, e.g., recording system, electrode, microscope.
    """

    __nwbfields__ = (
        'name',
        'description',
        'manufacturer',
        'model_number',
        'model_name',
        'serial_number',
    )

    @docval(
        {'name': 'name', 'type': str, 'doc': 'the name of this device'},
        {'name': 'description', 'type': str,
         'doc': ("Description of the device as free-form text. If there is any software/firmware associated "
                 "with the device, the names and versions of those can be added to `NWBFile.was_generated_by`."),
         'default': None},
        {'name': 'manufacturer', 'type': str,
         'doc': ("The name of the manufacturer of the device, e.g., Imec, Plexon, Thorlabs."),
         'default': None},
        {'name': 'model_number', 'type': str,
         'doc': ('The model number (or part/product number) of the device, e.g., PRB_1_4_0480_1, '
                 'PLX-VP-32-15SE(75)-(260-80)(460-10)-300-(1)CON/32m-V, BERGAMO.'),
         'default': None},
        {'name': 'model_name', 'type': str,
         'doc': ('The model name of the device, e.g., Neuropixels 1.0, V-Probe, Bergamo III.'),
         'default': None},
        {'name': 'serial_number', 'type': str,
         'doc': 'The serial number of the device.',
         'default': None},
    )
    def __init__(self, **kwargs):
        description, manufacturer, model_number, model_name, serial_number = popargs(
            'description', 'manufacturer', 'model_number', 'model_name', 'serial_number', kwargs)
        super().__init__(**kwargs)
        self.description = description
        self.manufacturer = manufacturer
        self.model_number = model_number
        self.model_name = model_name
        self.serial_number = serial_number
