from .spec import TypeMap

def process_spec(builder, spec, value):
    if isinstance(spec, AttributeSpec):
        builder.add_attribute(spec.name, value)
    else:
        if isinstance(spec, DatasetSpec):
            builder.add_dataset(spec.name, value)
        elif isinstance(spec, GroupSpec):
            #TODO: this assumes that value is a Container
            # This is where spec.name comes from -- Containers have a name value
            group_name = spec.name
            attrs = [value]
            if any(isinstance(value, t) for t in (list, tuple, dict)):
                attrs = value
                if isinstance(value, dict):
                    attrs = value.values()
            for container in attrs:
                builder.add_group(container_map.get_group_name(container),
                                  render_container(container, TypeMap.get_map(container)))

def render_container(container, attr_map):
    builder = GroupBuilder()
    children_attributes = dict()
    
    for attr_name in container.nwb_fields:
        tmp_builder = builder
        attr = getattr(container, attr_name)
        #TODO: add something to handle links
        attr_spec = attr_map.get_spec(attr_name)

        # add this after we created the parent
        if attr_spec.parent != attr_map.spec:
            child_attributes.append(attr_name)
        process_spec(tmp_builder, attr_spec, attr)
        
    # add attributes that apply to subgroups and datasets
    for attr_name in children_attributes:
        attr = getattr(container, attr_name)
        attr_spec = attr_map.get_spec(attr_name)
        parent_spec_attr_name = attr_map.get_attribute(attr_spec.parent)
        parent_builder_name = attr_spec.parent.name 
        # TODO: add check for wildcard name
        if parent_builder_name in builder:
            tmp_builder = builder.get(parent_builder_name)
        else:
            #TODO: handle case where parent spec not created yet
            pass
        process_spec(tmp_builder, attr_spec, attr)
        
    return builder


