from warnings import warn

from .. import register_map
from ..device import Device, DeviceModel
from .core import NWBContainerMapper

# Tutorial section that demonstrates replacing a read-only remapped DeviceModel (whose name contains
# characters not allowed in NWB object names) with a new DeviceModel that has a valid name.
DEVICE_MODEL_TUTORIAL_URL = (
    "https://pynwb.readthedocs.io/en/stable/tutorials/general/add_remove_containers.html"
    "#upgrading-a-legacy-device-model-string-to-a-devicemodel"
)


def _name_has_invalid_chars(name):
    """Return True if ``name`` contains a character that is not allowed in an NWB object name."""
    return "/" in name or ":" in name


def _construct_legacy_device_model(**kwargs):
    """Construct a DeviceModel in HDMF construct mode.

    Reading a legacy file where ``Device.model`` is a string remaps that string to a ``DeviceModel``
    whose name is the original string. Construct mode bypasses the ``AbstractContainer`` name
    validation so legacy names containing ``/`` or ``:`` (which are not allowed in newly created
    object names) can still be read. Such a DeviceModel is read-only: writing or exporting it raises
    an error in ``DeviceModelMapper.build`` because the invalid name would silently create nested
    HDF5 groups.
    """
    model = DeviceModel.__new__(DeviceModel, in_construct_mode=True)
    model.__init__(**kwargs)
    model._in_construct_mode = False
    return model


@register_map(DeviceModel)
class DeviceModelMapper(NWBContainerMapper):
    """Custom mapper that guards against writing a DeviceModel with an invalid name.

    A DeviceModel remapped from a legacy ``Device.model`` string (see :class:`DeviceMapper`) keeps
    the original string as its name, which can contain ``/`` or ``:``. Those characters are
    interpreted as HDF5 path separators on write, silently splitting the model into nested groups
    and corrupting the file. Building such a DeviceModel raises an actionable error instead.
    """

    def build(self, *args, **kwargs):
        container = args[0] if args else kwargs.get("container")
        if container is not None and _name_has_invalid_chars(container.name):
            raise ValueError(
                f'Cannot write DeviceModel "{container.name}": its name contains a "/" or ":", '
                "which are not allowed in NWB object names. This DeviceModel was likely remapped "
                "from a legacy Device.model string when reading an older file and is read-only. To "
                "write or export the data, create a new DeviceModel with a valid name and assign it to "
                f"Device.model. See {DEVICE_MODEL_TUTORIAL_URL} for an example."
            )
        return super().build(*args, **kwargs)


@register_map(Device)
class DeviceMapper(NWBContainerMapper):
    """
    Custom mapper for Device objects to handle known schema conflicts between core schema and extensions.

    This mapper detects when extensions define Device.model as a string attribute instead of
    a link to DeviceModel, or when extensions define their own DeviceModel type.
    """

    @NWBContainerMapper.constructor_arg("model")
    def model_carg(self, builder, manager):
        """
        Handle different model mapping strategies based on detected schema conflicts.

        Args:
            builder: The GroupBuilder for the Device
            manager: The BuildManager

        Returns:
            The appropriate model object or value based on the mapping strategy
        """
        model_builder = builder.get('model')
        if isinstance(model_builder, str):
            msg = (
                'Device.model was detected as a string, but NWB 2.9 specifies Device.model as a link to a DeviceModel. '
                f'Remapping "{model_builder}" to a new DeviceModel.'
            )
            if _name_has_invalid_chars(model_builder):
                msg += (
                    ' Because the model name contains a "/" or ":", which are not allowed in NWB object names, the '
                    'remapped DeviceModel is read-only and the file cannot be written or exported until it is '
                    'replaced. To write/export the data, create a new DeviceModel with a valid name and assign it to '
                    f'Device.model. See {DEVICE_MODEL_TUTORIAL_URL} for an example.'
                )
            warn(msg, stacklevel=3)

            # replace the model string with a DeviceModel object using the model name and device attributes
            device_model_attributes = dict(name=model_builder,
                                           description=builder.attributes.get('description'),
                                           manufacturer=builder.attributes.get('manufacturer', ''),
                                           model_number=builder.attributes.get('model_number'))
            model = _construct_legacy_device_model(**device_model_attributes)

            return model

        return None


    def __new_container__(self, cls, container_source, parent, object_id, **kwargs):
        # Override ObjectMapper.__new_container__ to handle the case where the Device.model argument
        # is not a DeviceModel, which can happen in extensions written to be compatible with NWB<2.9.
        # The original Device.model object will be accessible under a new attribute name based on the
        # extension namespace.
        model = kwargs.get('model', None)

        if model is None or isinstance(model, DeviceModel):
            device_obj = super().__new_container__(cls, container_source, parent, object_id, **kwargs)
        else:
            # create device object without model
            kwargs.pop('model')
            device_obj = super().__new_container__(cls, container_source, parent, object_id, **kwargs)

            # add the conflicting Device.model object as a new attribute on Device
            # e.g. Device.model in the file -> Device.ndx_optogenetics_model in the python object
            warn(f'The model attribute of the Device "{device_obj.name}" was detected as a non-DeviceModel '
                 f'object. Data associated with this object can be accessed at '
                 f'"nwbfile.devices["{device_obj.name}"].{model.namespace.replace("-", "_")}_model"',
                 stacklevel=2)
            setattr(device_obj, f"{model.namespace.replace('-', '_')}_model", model)

        return device_obj
