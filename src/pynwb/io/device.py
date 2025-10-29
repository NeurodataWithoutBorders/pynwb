from warnings import warn

from .. import register_map
from ..device import Device, DeviceModel
from .core import NWBContainerMapper


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
            warn(
                'Device.model was detected as a string, but NWB 2.9 specifies Device.model as a link to a DeviceModel. '
                f'Remapping "{model_builder}" to a new DeviceModel.',
                 stacklevel=3)

            # replace the model string with a DeviceModel object using the model name and device attributes 
            device_model_attributes = dict(name=model_builder,
                                           description=builder.attributes.get('description'),
                                           manufacturer=builder.attributes.get('manufacturer', ''),
                                           model_number=builder.attributes.get('model_number'))
            model = DeviceModel(**device_model_attributes)
        
            return model

        return None
    
      
    def __new_container__(self, cls, container_source, parent, object_id, **kwargs):
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
