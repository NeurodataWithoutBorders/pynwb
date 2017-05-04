import re
import sys

from ..utils import docval, getargs, ExtenderMeta, get_docval
from ..container import Container
from ..spec import Spec, AttributeSpec, DatasetSpec, GroupSpec, LinkSpec, NAME_WILDCARD, SpecCatalog, NamespaceCatalog
from .builders import DatasetBuilder, GroupBuilder, LinkBuilder, Builder

@docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'the parent spec to search'},
        {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to get the sub-specification for'},
        is_method=False)
def get_subspec(**kwargs):
    '''
    Get the specification from this spec that corresponds to the given builder
    '''
    spec, builder = getargs('spec', 'builder', kwargs)
    if isinstance(builder, DatasetBuilder):
        subspec = spec.get_dataset(builder.name)
    else:
        subspec = spec.get_group(builder.name)
    if subspec is None:
        ndt = builder.attributes.get('neurodata_type')
        if ndt is not None:
            subspec = spec.get_neurodata_type(ndt)
    return subspec

class BuildManager(object):
    """
    A class for managing builds of Containers
    """

    def __init__(self, type_map):
        self.__builders = dict()
        self.__containers = dict()
        self.__type_map = type_map

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"})
    def build(self, **kwargs):
        """ Build the GroupBuilder for the given Container"""
        container = getargs('container', kwargs)
        container_id = self.__conthash__(container)
        result = self.__builders.get(container_id)
        if result is None:
            result = self.__type_map.build(container, self)
            self.prebuilt(container, result)
        return result

    @docval({"name": "container", "type": Container, "doc": "the Container to save as prebuilt"},
            {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the Builder representation of the given container'})
    def prebuilt(self, **kwargs):
        ''' Save the Builder for a given Container for future use '''
        container, builder = getargs('container', 'builder', kwargs)
        container_id = self.__conthash__(container)
        self.__builders[container_id] = builder
        builder_id = self.__bldrhash__(builder)
        self.__containers[builder_id] = container

    def __conthash__(self, obj):
        return id(obj)

    def __bldrhash__(self, obj):
        return id(obj)

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to construct the Container from'})
    def construct(self, **kwargs):
        """ Construct the Container represented by the given builder """
        builder = getargs('builder', kwargs)
        if isinstance(builder, LinkBuilder):
            builder = bulder.target
        builder_id = self.__bldrhash__(builder)
        result = self.__containers.get(builder_id)
        if result is None:
            result = self.__type_map.construct(builder, self)
            self.prebuilt(result, builder)
        return result

    @docval({'name': 'builder', 'type': Builder, 'doc': 'the Builder to get the class object for'})
    def get_cls(self, **kwargs):
        ''' Get the class object for the given Builder '''
        builder = getargs('builder', kwargs)
        #return self.__type_map.get_cls(builder.attributes.get('neurodata_type'))
        return self.__type_map.get_cls(builder)

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            returns='The name a Builder should be given when building this container', rtype=str)
    def get_builder_name(self, **kwargs):
        ''' Get the name a Builder should be given '''
        container = getargs('container', kwargs)
        return self.__type_map.get_builder_name(container)

class TypeMap(object):

    #@docval({'name': 'catalog', 'type': SpecCatalog, 'doc': 'a catalog of existing specifications'})
    @docval({'name': 'namespaces', 'type': NamespaceCatalog, 'doc': 'the NamespaceCatalog to use'})
    def __init__(self, **kwargs):
        namespaces = getargs('namespaces', kwargs)
        self.__map_types = dict()
        self.__namespaces = namespaces
        self.__mappers = dict()     ## already constructed ObjectMapper classes
        self.__mapper_cls = dict()  ## the ObjectMapper class to use for each container type
        self.__container_types = dict()
        self.__neurodata_types = dict()

    def __get_neurodata_type(self, obj):
        ret = obj.get('neurodata_type')
        if ret is None:
            raise ValueError("builder '%s' is does not have a neurodata_type" % builder.name)
        return ret

    def __get_namespace(self, bldr):
        return bldr.get('namespace', self.__namespaces.default_namespace)

    @docval({'name': 'builder', 'type': Builder, 'doc': 'the Builder object to get the corresponding Container class for'})
    def get_cls(self, **kwargs):
        builder = getargs('builder', kwargs)
        neurodata_type = self.__get_neurodata_type(builder)
        namespace = self.__get_namespace(builder)
        if namespace not in self.__container_types:
            raise ValueError("no neurodata_types from namespace '%s' have been mapped" % namespace)
        if neurodata_type not in self.__container_types[namespace]:
            raise ValueError("no neurodata_type '%s' from namespace '%s has been mapped'" % (neurodata_type, namespace))
        container_cls = self.__container_types[namespace][neurodata_type]
        return container_cls

    @docval({'name': 'obj', 'type': (Container, Builder), 'doc': 'the object to get the ObjectMapper for'},
            returns='the ObjectMapper to use for mapping the given object', rtype='ObjectMapper')
    def get_map(self, **kwargs):
        """ Return the ObjectMapper object that should be used for the given container """
        obj = getargs('obj', kwargs)
        # get the container class, and namespace/neurodata_type
        if isinstance(obj, Container):
            container_cls = obj.__class__
            namespace, neurodata_type = self.__neurodata_types.get(container_cls, (None, None))
            if namespace is None:
                raise ValueError("class %s does not mapped to a neurodata_type" % container_cls)
        else:
            neurodata_type = self.__get_neurodata_type(obj)
            namespace = self.__get_namespace(obj)
            container_cls = self.get_cls(obj)
        # now build the ObjectMapper class
        for cls in container_cls.__mro__:
            mapper = self.__mappers.get(cls)
            if mapper is None: # we haven't yet constructed a mapper for this type
                mapper_cls = self.__mapper_cls.get(cls)
                if mapper_cls is None:
                    continue
                spec = self.__namespaces.get_spec(namespace, neurodata_type)
                mapper = mapper_cls(spec)
                self.__mappers[cls] = mapper
                break
            else:
                break
        if mapper is None:
            raise ValueError("No ObjectMapper found for class %s, namespace '%s', neurodata_type '%s'" % (container_cls, namespace, neurodata_type))
        return mapper

    @docval({"name": "namespace", "type": str, "doc": "the namespace containing the neurodata_type to map the class to"},
            {"name": "neurodata_type", "type": str, "doc": "the neurodata_type to mape the class to"},
            {"name": "container_cls", "type": type, "doc": "the class to map to the specified neurodata_type"})
    def register_container_type(self, **kwargs):
        namespace, neurodata_type, container_cls = getargs('namespace', 'neurodata_type', 'container_cls', kwargs)
        self.__container_types.setdefault(namespace, dict())
        self.__container_types[namespace][neurodata_type] = container_cls
        self.__neurodata_types[container_cls] = (namespace, neurodata_type)

    @docval({"name": "container_cls", "type": type, "doc": "the Container class for which the given ObjectMapper class gets used for"},
            {"name": "mapper_cls", "type": type, "doc": "the ObjectMapper class to use to map"})
    def register_map(self, **kwargs):
        container_cls, mapper_cls = getargs('container_cls', 'mapper_cls', kwargs)
        self.__mapper_cls[container_cls] = mapper_cls

#    def get_registered_types(self):
#        """ Return all Container types that have a map specified """
#        return tuple(self.__maps.keys())
#
    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            {"name": "manager", "type": BuildManager, "doc": "the BuildManager to use for managing this build", 'default': None})
    def build(self, **kwargs):
        """ Build the GroupBuilder for the given Container"""
        container, manager = getargs('container', 'manager', kwargs)
        if manager is None:
            manager = BuildManager(self)
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.build(container, manager)

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to construct the Container from'},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager for constructing', 'default': None})
    def construct(self, **kwargs):
        """ Construct the Container represented by the given builder """
        builder, build_manager = getargs('builder', 'build_manager', kwargs)
        if build_manager is None:
            build_manager = BuildManager(self)
        attr_map = self.get_map(builder)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for builder of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.construct(builder, build_manager)

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            returns='The name a Builder should be given when building this container', rtype=str)
    def get_builder_name(self, **kwargs):
        ''' Get the name a Builder should be given '''
        container = getargs('container', kwargs)
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.get_builder_name(container)

class DecExtenderMeta(ExtenderMeta):

    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return {
            'const_arg': metacls.const_arg ,
            'is_const_arg': metacls.is_const_arg,
            'get_cargname': metacls.get_cargname,
        }

#    __obj_attr = '__obj_attr__'
#    @classmethod
#    def obj_attr(cls, name):
#        def _dec(func):
#            setattr(func, cls.__obj_attr, name)
#            return func
#        return _dec
#
#    @classmethod
#    def is_attr(cls, attr_val):
#        return hasattr(attr_val, cls.__obj_attr)
#
#    @classmethod
#    def get_obj_attr(cls, attr_val):
#        return getattr(attr_val, cls.__obj_attr)
#
    __const_arg = '__const_arg__'
    @classmethod
    def const_arg(cls, name):
        def _dec(func):
            setattr(func, cls.__const_arg, name)
            return func
        return _dec

    @classmethod
    def is_const_arg(cls, attr_val):
        return hasattr(attr_val, cls.__const_arg)

    @classmethod
    def get_cargname(cls, attr_val):
        return getattr(attr_val, cls.__const_arg)

class ObjectMapper(object, metaclass=DecExtenderMeta):

    _property = "__item_property__"
    @ExtenderMeta.post_init
    def __gather_procedures(cls, name, bases, classdict):
        cls.const_args = dict()
        #cls.const_args['name'] = lambda self, builder: builder.name
        for name, func in filter(lambda tup: cls.is_const_arg(tup[1]), cls.__dict__.items()):
            cls.const_args[cls.get_cargname(func)] = getattr(cls, name)

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications """
        spec = getargs('spec', kwargs)
        self.__spec = spec
        self.__spec2attr = dict()
        self.__spec2carg = dict()
        self.__map_spec(spec)

    @property
    def spec(self):
        ''' the Spec used in this ObjectMapper '''
        return self.__spec

    @const_arg('name')
    def get_container_name(self, builder):
        return builder.name

    @staticmethod
    def __convert_name(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        ret = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        if ret[-1] != 's':
            ret += 's'
        return ret

    def __map_spec(self, spec):
        for subspec in spec.attributes:
            self.__map_spec_helper(subspec)
        self.__map_spec_helper(spec)
        if isinstance(spec, GroupSpec):
            for subspec in spec.datasets:
                self.__map_spec(subspec)
            for subspec in spec.groups:
                if subspec.neurodata_type_def is None:
                    self.__map_spec(subspec)

    def __map_spec_helper(self, spec):
        if spec.name != NAME_WILDCARD:
            self.map_attr(spec.name, spec)
            self.map_const_arg(spec.name, spec)
        else:
            name = self.__convert_name(spec.neurodata_type)
            self.map_attr(name, spec)
            self.map_const_arg(name, spec)

    @docval({"name": "attr_name", "type": str, "doc": "the name of the object to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_attr(self, **kwargs):
        """ Map an attribute to spec. Use this to override default behavior """
        attr_name, spec = getargs('attr_name', 'spec', kwargs)
        if hasattr(spec, 'name') and spec.name is not None:
            n = spec.name
        elif hasattr(spec, 'neurodata_type') and spec.neurodata_type is not None:
            n = spec.neurodata_type
        self.__spec2attr[spec] = attr_name

    @docval({"name": "const_arg", "type": str, "doc": "the name of the constructor argument to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_const_arg(self, **kwargs):
        """ Map an attribute to spec. Use this to override default behavior """
        const_arg, spec = getargs('const_arg', 'spec', kwargs)
        self.__spec2carg[spec] = const_arg

    @docval({"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def unmap(self, **kwargs):
        """ Removing any mapping for a specification. Use this to override default mapping """
        spec = getargs('spec', kwargs)
        self.__spec2attr.pop(spec, None)
        self.__spec2carg.pop(spec, None)

    def __get_override_carg(self, name, builder):
        if name in self.const_args:
            #func = getattr(self, self.const_args[name])
            func = self.const_args[name]
            return func(self, builder)
        return None

    @docval({"name": "spec", "type": Spec, "doc": "the spec to get the attribute for"},
            returns='the attribute name', rtype=str)
    def get_attribute(self, **kwargs):
        ''' Get the object attribute name for the given Spec '''
        spec = getargs('spec', kwargs)
        return self.__spec2attr.get(spec, None)

    @docval({"name": "spec", "type": Spec, "doc": "the spec to get the attribute value for"},
            {"name": "container", "type": Container, "doc": "the container to get the attribute value from"},
            returns='the value of the attribute')
    def get_attr_value(self, **kwargs):
        ''' Get the value of the attribute corresponding to this spec from the given container '''
        spec, container = getargs('spec', 'container', kwargs)
        attr_name = self.get_attribute(spec)
        if attr_name is None:
            return None
        attr_val = getattr(container, attr_name, None)
        if attr_val is None:
            return None
        else:
            return self.__convert_value(attr_val, spec)

    def __convert_value(self, value, spec):
        ret = value
        if isinstance(spec, AttributeSpec):
            if 'text' in spec.dtype:
                if spec.dims is not None:
                    ret =  list(map(str, value))
                else:
                    ret = str(value)
        elif isinstance(spec, DatasetSpec):
            if 'text' in spec.dtype:
                if spec.dims is not None:
                    ret =  list(map(str, value))
                else:
                    ret = str(value)
        return ret

    @docval({"name": "spec", "type": Spec, "doc": "the spec to get the constructor argument for"},
            returns="the name of the constructor argument", rtype=str)
    def get_const_arg(self, **kwargs):
        ''' Get the constructor argument for the given Spec '''
        spec = getargs('spec', kwargs)
        return self.__spec2carg.get(spec, None)

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            {"name": "manager", "type": BuildManager, "doc": "the BuildManager to use for managing this build"},
            {"name": "parent", "type": Builder, "doc": "the parent of the resulting Builder", 'default': None},
            returns="the Builder representing the given Container", rtype=Builder)
    def build(self, **kwargs):
        ''' Convert an Container to a Builder representation '''
        container, manager, parent = getargs('container', 'manager', 'parent', kwargs)
        name = manager.get_builder_name(container)
        if isinstance(self.__spec, GroupSpec):
            builder = GroupBuilder(name, parent=parent)
            self.__add_datasets(builder, self.__spec.datasets, container, manager)
            self.__add_groups(builder, self.__spec.groups, container, manager)
        else:
            builder = DatasetBuilder(name, parent=parent)
        self.__add_attributes(builder, self.__spec.attributes, container)
        builder.set_attribute('neurodata_type', container.neurodata_type)
        return builder

    def __is_null(self, item):
        if item is None:
            return True
        else:
            if any(isinstance(item, t) for t in (list, tuple, dict, set)):
                return len(item) == 0
        return False

    def __add_attributes(self, builder, attributes, container):
        for spec in attributes:
            attr_value = self.get_attr_value(spec, container)
            #if self.__is_null(attr_value):
            if not attr_value:
                if spec.value is not None:
                    attr_value = spec.value
                else:
                    continue
            builder.set_attribute(spec.name, attr_value)

    def __add_datasets(self, builder, datasets, container, build_manager):
        for spec in datasets:
            attr_value = self.get_attr_value(spec, container)
            #if self.__is_null(attr_value):
            if not attr_value:
                continue
            if spec.neurodata_type is None:
                sub_builder = builder.add_dataset(spec.name, attr_value)
                self.__add_attributes(sub_builder, spec.attributes, container)
            else:
                self.__add_containers(builder, spec, attr_value, build_manager)

    def __add_groups(self, builder, groups, container, build_manager):
        for spec in groups:
            if spec.neurodata_type is None:
                # we don't need to get attr_name since any named
                # group does not have the concept of value
                sub_builder = GroupBuilder(spec.name)
                self.__add_attributes(sub_builder, spec.attributes, container)
                self.__add_datasets(sub_builder, spec.datasets, container, build_manager)

                # handle subgroups that are not Containers
                attr_name = self.get_attribute(spec)
                if attr_name is not None:
                    attr_value = getattr(container, attr_name, None)
                    attr_value = self.get_attr_value(spec, container)
                    if any(isinstance(attr_value, t) for t in (list, tuple, set, dict)):
                        it = iter(attr_value)
                        if isinstance(attr_value, dict):
                            it = iter(attr_value.values())
                        for item in it:
                            if isinstance(item, Container):
                                self.__add_containers(sub_builder, spec, item, build_manager)
                        #continue
                self.__add_groups(sub_builder, spec.groups, container, build_manager)
                empty = sub_builder.is_empty()
                if not empty or (empty and isinstance(spec.quantity, int)):
                    builder.set_group(sub_builder)
            else:
                if spec.neurodata_type_def is not None:
                    attr_name = self.get_attribute(spec)
                    if attr_name is not None:
                        attr_value = getattr(container, attr_name, None)
                        if attr_value is not None:
                            self.__add_containers(builder, spec, attr_value, build_manager)
                else:
                    attr_name = self.get_attribute(spec)

                    attr_value = getattr(container, attr_name, None)
                    if attr_value is not None:
                        self.__add_containers(builder, spec, attr_value, build_manager)

    def __add_containers(self, builder, spec, value, build_manager):
        if isinstance(value, Container):
            rendered_obj = build_manager.build(value)
            name = build_manager.get_builder_name(value)
            # use spec to determine what kind of HDF5
            # object this Container corresponds to
            if isinstance(spec, LinkSpec):
                builder.set_link(LinkBuilder(name, rendered_obj, builder))
            elif isinstance(spec, DatasetSpec):
                builder.set_dataset(rendered_obj)
            else:
                builder.set_group(rendered_obj)
        else:
            if any(isinstance(value, t) for t in (list, tuple)):
                values = value
            elif isinstance(value, dict):
                values = value.values()
            else:
                msg = ("received %s, expected Container - 'value' "
                       "must be an Container a list/tuple/dict of "
                       "Containers if 'spec' is a GroupSpec")
                raise ValueError(msg % value.__class__.__name__)
            for container in values:
                self.__add_containers(builder, spec, container, build_manager)

    def __get_subspec_values(self, builder, spec, manager):
        ret = dict()
        for h5attr_name, h5attr_val in builder.attributes.items():
            subspec = spec.get_attribute(h5attr_name)
            if subspec is None:
                continue
            ret[subspec] = h5attr_val
        if isinstance(builder, GroupBuilder):
            for sub_builder_name, sub_builder in builder.items():
                # GroupBuilder.items will return attributes as well, need to skip non Builder items
                if not isinstance(sub_builder, Builder):
                    continue
                subspec = get_subspec(spec, sub_builder)
                if subspec is not None:
                    if 'neurodata_type' in sub_builder.attributes:
                        val = manager.construct(sub_builder)
                        if subspec.is_many():
                            if subspec in ret:
                               ret[subspec].append(val)
                            else:
                                ret[subspec] = [val]
                        else:
                            ret[subspec] = val
                    else:
                        result = self.__get_subspec_values(sub_builder, subspec, manager)
                        ret.update(result)
        else:
            ret[spec] = builder.data
        return ret

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to construct the Container from'},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager for this build'})
    def construct(self, **kwargs):
        ''' Construct an Container from the given Builder '''
        builder, manager = getargs('builder', 'manager', kwargs)
        cls = manager.get_cls(builder)
        #cls = self.get_cls(builder)
        # gather all subspecs
        subspecs = self.__get_subspec_values(builder, self.spec, manager)
        # get the constructor argument each specification corresponds to
        const_args = dict()
        for subspec, value in subspecs.items():
            const_arg = self.get_const_arg(subspec)
            if const_arg is not None:
                const_args[const_arg] = value
        # build args and kwargs for the constructor
        args = list()
        kwargs = dict()
        for const_arg in get_docval(cls.__init__):
            argname = const_arg['name']
            override = self.__get_override_carg(argname, builder)
            if override:
                val = override
            elif argname in const_args:
                val = const_args[argname]
            else:
                continue
            if 'default' in const_arg:
                kwargs[argname] = val
            else:
                args.append(val)
        return cls(*args, **kwargs)

    def get_builder_name(self, container):
        if self.__spec.name != NAME_WILDCARD:
            ret = self.__spec.name
        else:
            ret = container.name
        return ret
