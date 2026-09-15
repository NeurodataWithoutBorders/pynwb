from hdmf.utils import docval, popargs, AllowPositional
import warnings

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer

__all__ = ['Device', 'DeviceModel']

@register_class('Device', CORE_NAMESPACE)
class Device(NWBContainer):
    """
    Metadata about a data acquisition device, e.g., recording system, electrode, microscope.
    Link to a DeviceModel.model to represent information about the model of the device.
    """

    __nwbfields__ = (
        'name',
        'description',
        'manufacturer',
        'model_number',
        'model_name',
        'serial_number',
        'model',
    )

    @docval(
        {'name': 'name', 'type': str, 'doc': 'the name of this device'},
        {'name': 'description', 'type': str,
         'doc': ("Description of the device as free-form text. If there is any software/firmware associated "
                 "with the device, the names and versions of those can be added to `NWBFile.was_generated_by`."),
         'default': None},
        {'name': 'manufacturer', 'type': str,
         'doc': ("DEPRECATED. The name of the manufacturer of the device, e.g., Imec, Plexon, Thorlabs. "
                 "Instead of using this field, store the value in DeviceModel.manufacturer and link to that "
                 "DeviceModel from this Device."),
         'default': None},
        {'name': 'model_number', 'type': str,
         'doc': ('DEPRECATED. The model number (or part/product number) of the device, e.g., PRB_1_4_0480_1, '
                 'PLX-VP-32-15SE(75)-(260-80)(460-10)-300-(1)CON/32m-V, BERGAMO. '
                 'Instead of using this field, store the value in DeviceModel.model_number and link to that '
                 'DeviceModel from this Device. '),
         'default': None},
        {'name': 'model_name', 'type': str,
         'doc': ('DEPRECATED. The model name of the device, e.g., Neuropixels 1.0, V-Probe, Bergamo III. '
                 'Instead of using this field, storing the value in DeviceModel.name and link to that '
                 'DeviceModel from this Device.'),
         'default': None},
        {'name': 'serial_number', 'type': str, 'doc': 'The serial number of the device.', 'default': None},
        {'name': 'model', 'type': 'DeviceModel', 'doc': 'The model of the device.', 'default': None},
         allow_positional=AllowPositional.WARNING,
    )
    def __init__(self, **kwargs):
        description, manufacturer, model_number, model_name, serial_number, model = popargs(
            'description', 'manufacturer', 'model_number', 'model_name', 'serial_number', 'model', kwargs)
        if model_number is not None:
            warnings.warn(
                "The 'model_number' field is deprecated. Instead, use DeviceModel.model_number and link to that "
                "DeviceModel from this Device.",
                DeprecationWarning,
                stacklevel=2
            )
        if manufacturer is not None:
            warnings.warn(
                "The 'manufacturer' field is deprecated. Instead, use DeviceModel.manufacturer and link to that "
                "DeviceModel from this Device.",
                DeprecationWarning,
                stacklevel=2
            )
        if model_name is not None:
            warnings.warn(
                "The 'model_name' field is deprecated. Instead, use DeviceModel.name and link to that "
                "DeviceModel from this Device.",
                DeprecationWarning,
                stacklevel=2
            )
        super().__init__(**kwargs)
        self.description = description
        self.manufacturer = manufacturer
        self.model_number = model_number
        self.model_name = model_name
        self.serial_number = serial_number
        self.model = model


@register_class('DeviceModel', CORE_NAMESPACE)
class DeviceModel(NWBContainer):
    """
    Model properties of a data acquisition device, e.g., recording system, electrode, microscope.
    """

    __nwbfields__ = (
        'manufacturer',
        'model_number',
        'description',
    )

    @docval(
        {'name': 'name', 'type': str, 'doc': 'The name of this device model'},
        {'name': 'manufacturer', 'type': str,
         'doc': ("The name of the manufacturer of the device, e.g., Imec, Plexon, Thorlabs.")},
        {'name': 'model_number', 'type': str,
         'doc': ('The model number (or part/product number) of the device, e.g., PRB_1_4_0480_1, '
                 'PLX-VP-32-15SE(75)-(260-80)(460-10)-300-(1)CON/32m-V, BERGAMO.'),
         'default': None},
        {'name': 'description', 'type': str,
         'doc': ("Description of the device model as free-form text."),
         'default': None},
         allow_positional=AllowPositional.ERROR,
    )
    def __init__(self, **kwargs):
        manufacturer, model_number, description = popargs('manufacturer', 'model_number', 'description', kwargs)
        super().__init__(**kwargs)
        self.manufacturer = manufacturer
        self.model_number = model_number
        self.description = description
