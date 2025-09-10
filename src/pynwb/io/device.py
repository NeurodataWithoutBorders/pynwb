from hdmf.build import ObjectMapper
from hdmf.utils import docval, getargs
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

    def __init__(self, spec):
        super().__init__(spec)
        self._model_conflict_detected = False
        self._model_mapping_strategy = 'core'  # 'core', 'extension_string', 'extension_custom'
        self._detect_model_conflicts(spec)  # TODO - this is already checked when the namespace is loaded - better way to propagate from there?

    def _detect_model_conflicts(self, spec):
        """
        Detect conflicts in Device.model definition between core schema and extensions.
        
        Args:
            spec: The GroupSpec for Device
        """
        # Check if model is defined as a link (core schema) or attribute (extension)
        model_link = None
        model_attr = None
        
        # Look for model as a link
        for link in spec.links:
            if link.name == 'model':
                model_link = link
                break
        
        # Look for model as an attribute
        model_attr = spec.get_attribute('model')
        
        self._model_mapping_strategy = 'core' #default behavior
        if model_link is not None and model_attr is None:
            if model_link and model_attr:
                # Both link and attribute defined - this is a conflict
                self._model_conflict_detected = True
                self._model_mapping_strategy = 'conflict'
            elif model_attr and not model_link:
                # Only attribute defined - extension overrides core
                self._model_conflict_detected = True
                if hasattr(model_attr, 'dtype') and model_attr.dtype == 'text':
                    self._model_mapping_strategy = 'extension_string'
                else:
                    self._model_mapping_strategy = 'extension_custom'


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
        if model_builder is None:
            return None
            
        if self._model_mapping_strategy == 'core':
            # Standard core schema: model is a link to DeviceModel
            if hasattr(model_builder, 'builder'):
                # This is a LinkBuilder
                target_builder = model_builder.builder
                if target_builder.parent is not None:
                    return manager.construct(target_builder)
                else:
                    # External link case
                    return target_builder.data
            else:
                # Direct reference to DeviceModel
                return manager.construct(model_builder)
                
        elif self._model_mapping_strategy == 'extension_string':
            # Extension schema: model is a string attribute
            if hasattr(model_builder, 'data'):
                return model_builder.data
            else:
                return str(model_builder)
                
        elif self._model_mapping_strategy == 'extension_custom':
            # Extension schema: model is a custom type
            return manager.construct(model_builder)
            
        elif self._model_mapping_strategy == 'conflict':
            # Conflict detected: prefer core schema behavior with warning
            warn(
                "Using core schema mapping for Device.model due to detected conflicts.",
                UserWarning,
                stacklevel=2
            )
            if hasattr(model_builder, 'builder'):
                target_builder = model_builder.builder
                if target_builder.parent is not None:
                    return manager.construct(target_builder)
                else:
                    return target_builder.data
            else:
                return manager.construct(model_builder)
        
        # Fallback to core behavior
        return manager.construct(model_builder) if model_builder else None

    @NWBContainerMapper.object_attr("model")
    def model_attr(self, container, manager):
        """
        Handle writing model attribute based on schema type and mapping strategy.
        
        Args:
            container: The Device container
            manager: The BuildManager
            
        Returns:
            The appropriate model representation for writing
        """
        model = container.fields.get('model')
        if model is None:
            return None
            
        if self._model_mapping_strategy == 'core':
            # Standard core schema: model should be a DeviceModel object
            if isinstance(model, DeviceModel):
                # Create a link to the DeviceModel
                from hdmf.build import LinkBuilder
                model_builder = manager.build(model)
                return LinkBuilder(model_builder, 'model')
            else:
                # Handle case where model is not a DeviceModel (backward compatibility)
                warn(
                    f"Device.model should be a DeviceModel object, got {type(model)}. "
                    "Consider updating to use DeviceModel.",
                    UserWarning,
                    stacklevel=2
                )
                return model
                
        elif self._model_mapping_strategy == 'extension_string':
            # Extension schema: model should be a string
            if isinstance(model, str):
                return model
            elif isinstance(model, DeviceModel):
                # Convert DeviceModel to string representation
                warn(
                    "Extension expects Device.model as string, but DeviceModel object provided. "
                    "Using DeviceModel name as string.",
                    UserWarning,
                    stacklevel=2
                )
                return model.name
            else:
                return str(model)
                
        elif self._model_mapping_strategy in ('extension_custom', 'conflict'):
            # Extension or conflict: try to handle appropriately
            return model
            
        # Fallback
        return model


@register_map(DeviceModel)
class DeviceModelMapper(NWBContainerMapper):
    """
    Custom mapper for DeviceModel objects to handle potential conflicts with extension schemas.
    
    This mapper ensures DeviceModel objects are properly handled even when extensions
    define their own DeviceModel types or when Device.model conflicts exist.
    """

    def __init__(self, spec):
        super().__init__(spec)
        self._extension_devicemodel_detected = False
        self._detect_extension_conflicts(spec)

    def _detect_extension_conflicts(self, spec):
        """
        Detect if this DeviceModel spec comes from an extension that might conflict with core.
        
        Args:
            spec: The GroupSpec for DeviceModel
        """
        # Check if this DeviceModel spec has non-standard attributes or structure
        # that might indicate it's from an extension
        
        # Core DeviceModel should have: manufacturer, model_number (optional), description (optional)
        expected_core_attrs = {'manufacturer', 'model_number', 'description'}
        actual_attrs = {attr.name for attr in spec.attributes}
        
        # If there are attributes beyond the core set, this might be an extension
        extra_attrs = actual_attrs - expected_core_attrs
        if extra_attrs:
            self._extension_devicemodel_detected = True
            warn(
                f"Extension DeviceModel detected with additional attributes: {extra_attrs}. "
                "Using extension-specific mapping.",
                UserWarning,
                stacklevel=3
            )
                

    @NWBContainerMapper.constructor_arg("manufacturer")
    def manufacturer_carg(self, builder, manager):
        """Handle manufacturer field construction with extension compatibility."""
        manufacturer_builder = builder.get('manufacturer')
        if manufacturer_builder is None:
            return None
        return manufacturer_builder.data if hasattr(manufacturer_builder, 'data') else manufacturer_builder

    @NWBContainerMapper.constructor_arg("model_number")
    def model_number_carg(self, builder, manager):
        """Handle model_number field construction with extension compatibility."""
        model_number_builder = builder.get('model_number')
        if model_number_builder is None:
            return None
        return model_number_builder.data if hasattr(model_number_builder, 'data') else model_number_builder

    @NWBContainerMapper.constructor_arg("description")
    def description_carg(self, builder, manager):
        """Handle description field construction with extension compatibility."""
        description_builder = builder.get('description')
        if description_builder is None:
            return None
        return description_builder.data if hasattr(description_builder, 'data') else description_builder
