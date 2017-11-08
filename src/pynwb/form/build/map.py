import re
import warnings
from collections import OrderedDict
from copy import copy

from six import with_metaclass, raise_from
from ..utils import docval, getargs, ExtenderMeta, get_docval, fmt_docval_args
from ..container import Container, Data, DataRegion
from ..spec import Spec, AttributeSpec, DatasetSpec, GroupSpec, LinkSpec, NAME_WILDCARD, NamespaceCatalog, RefSpec
from ..spec.spec import BaseStorageSpec
from .builders import DatasetBuilder, GroupBuilder, LinkBuilder, Builder, RegionBuilder


class BuildManager(object):
    """
    A class for managing builds of Containers
    """

    def __init__(self, type_map):
        self.__builders = dict()
        self.__containers = dict()
        self.__type_map = type_map

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            {"name": "source", "type": str,
             "doc": "the source of container being built i.e. file path", 'default': None})
    def build(self, **kwargs):
        """ Build the GroupBuilder for the given Container"""
        container = getargs('container', kwargs)
        container_id = self.__conthash__(container)
        result = self.__builders.get(container_id)
        if result is None:
            result = self.__type_map.build(container, self, source=getargs('source', kwargs))
            self.prebuilt(container, result)
        return result

    @docval({"name": "container", "type": Container, "doc": "the Container to save as prebuilt"},
            {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder),
             'doc': 'the Builder representation of the given container'})
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

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder),
             'doc': 'the builder to construct the Container from'})
    def construct(self, **kwargs):
        """ Construct the Container represented by the given builder """
        builder = getargs('builder', kwargs)
        if isinstance(builder, LinkBuilder):
            builder = builder.target
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
        return self.__type_map.get_cls(builder)

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            returns='The name a Builder should be given when building this container', rtype=str)
    def get_builder_name(self, **kwargs):
        ''' Get the name a Builder should be given '''
        container = getargs('container', kwargs)
        return self.__type_map.get_builder_name(container)

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'the parent spec to search'},
            {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder, LinkBuilder),
             'doc': 'the builder to get the sub-specification for'})
    def get_subspec(self, **kwargs):
        '''
        Get the specification from this spec that corresponds to the given builder
        '''
        spec, builder = getargs('spec', 'builder', kwargs)
        return self.__type_map.get_subspec(spec, builder)


_const_arg = '__constructor_arg'


@docval({'name': 'name', 'type': str, 'doc': 'the name of the constructor argument'},
        is_method=False)
def _constructor_arg(**kwargs):
    '''Decorator to override the default mapping scheme for a given constructor argument.

    Decorate ObjectMapper methods with this function when extending ObjectMapper to override the default
    scheme for mapping between Container and Builder objects. The decorated method should accept as its
    first argument the Builder object that is being mapped. The method should return the value to be passed
    to the target Container class constructor argument given by *name*.
    '''
    name = getargs('name', kwargs)

    def _dec(func):
        setattr(func, _const_arg, name)
        return func
    return _dec


_obj_attr = '__object_attr'


@docval({'name': 'name', 'type': str, 'doc': 'the name of the constructor argument'},
        is_method=False)
def _object_attr(**kwargs):
    '''Decorator to override the default mapping scheme for a given object attribute.

    Decorate ObjectMapper methods with this function when extending ObjectMapper to override the default
    scheme for mapping between Container and Builder objects. The decorated method should accept as its
    first argument the Container object that is being mapped. The method should return the child Builder
    object (or scalar if the object attribute corresponds to an AttributeSpec) that represents the
    attribute given by *name*.
    '''
    name = getargs('name', kwargs)

    def _dec(func):
        setattr(func, _obj_attr, name)
        return func
    return _dec


class ObjectMapper(with_metaclass(ExtenderMeta, object)):
    '''A class for mapping between Spec objects and Container attributes

    '''

    _const_arg = '__constructor_arg'

    @staticmethod
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the constructor argument'},
            is_method=False)
    def constructor_arg(**kwargs):
        '''Decorator to override the default mapping scheme for a given constructor argument.

        Decorate ObjectMapper methods with this function when extending ObjectMapper to override the default
        scheme for mapping between Container and Builder objects. The decorated method should accept as its
        first argument the Builder object that is being mapped. The method should return the value to be passed
        to the target Container class constructor argument given by *name*.
        '''
        name = getargs('name', kwargs)
        return _constructor_arg(name)

    _obj_attr = '__object_attr'

    @staticmethod
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the constructor argument'},
            is_method=False)
    def object_attr(**kwargs):
        '''Decorator to override the default mapping scheme for a given object attribute.

        Decorate ObjectMapper methods with this function when extending ObjectMapper to override the default
        scheme for mapping between Container and Builder objects. The decorated method should accept as its
        first argument the Container object that is being mapped. The method should return the child Builder
        object (or scalar if the object attribute corresponds to an AttributeSpec) that represents the
        attribute given by *name*.
        '''
        name = getargs('name', kwargs)
        return _object_attr(name)

    @staticmethod
    def __is_attr(attr_val):
        return hasattr(attr_val, _obj_attr)

    @staticmethod
    def __get_obj_attr(attr_val):
        return getattr(attr_val, _obj_attr)

    @staticmethod
    def __is_constructor_arg(attr_val):
        return hasattr(attr_val, _const_arg)

    @staticmethod
    def __get_cargname(attr_val):
        return getattr(attr_val, _const_arg)

    @ExtenderMeta.post_init
    def __gather_procedures(cls, name, bases, classdict):
        if hasattr(cls, 'constructor_args'):
            cls.constructor_args = copy(cls.constructor_args)
        else:
            cls.constructor_args = dict()
        if hasattr(cls, 'obj_attrs'):
            cls.obj_attrs = copy(cls.obj_attrs)
        else:
            cls.obj_attrs = dict()
        for name, func in cls.__dict__.items():
            if cls.__is_constructor_arg(func):
                cls.constructor_args[cls.__get_cargname(func)] = getattr(cls, name)
            elif cls.__is_attr(func):
                cls.obj_attrs[cls.__get_obj_attr(func)] = getattr(cls, name)

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec),
             'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications """
        spec = getargs('spec', kwargs)
        self.__spec = spec
        self.__data_type_key = spec.type_key()
        self.__spec2attr = dict()
        self.__attr2spec = dict()
        self.__spec2carg = dict()
        self.__carg2spec = dict()
        self.__map_spec(spec)

    def hack_get_subspec_values(self, *args, **kwargs):
        return self.__get_subspec_values(*args, **kwargs)

    @property
    def spec(self):
        ''' the Spec used in this ObjectMapper '''
        return self.__spec

    @_constructor_arg('name')
    def get_container_name(self, *args):
        builder = args[0]
        return builder.name

    @classmethod
    @docval({'name': 'spec', 'type': Spec, 'doc': 'the specification to get the name for'})
    def convert_dt_name(cls, **kwargs):
        '''Get the attribute name corresponding to a specification'''
        spec = getargs('spec', kwargs)
        if spec.data_type_def is not None:
            name = spec.data_type_def
        elif spec.data_type_inc is not None:
            name = spec.data_type_inc
        else:
            raise ValueError('found spec without name or data_type')
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        if name[-1] != 's' and spec.is_many():
            name += 's'
        return name

    @classmethod
    def __get_fields(cls, name_stack, all_names, spec):
        name = spec.name
        if spec.name is None:
            name = cls.convert_dt_name(spec)
        name_stack.append(name)
        if name in all_names:
            name = "_".join(name_stack)
        all_names[name] = spec
        if isinstance(spec, BaseStorageSpec):
            if not (spec.data_type_def is None and spec.data_type_inc is None):
                # don't get names for components in data_types
                return
            for subspec in spec.attributes:
                cls.__get_fields(name_stack, all_names, subspec)
            if isinstance(spec, GroupSpec):
                for subspec in spec.datasets:
                    cls.__get_fields(name_stack, all_names, subspec)
                for subspec in spec.groups:
                    cls.__get_fields(name_stack, all_names, subspec)
                for subspec in spec.links:
                    cls.__get_fields(name_stack, all_names, subspec)
        name_stack.pop()

    @classmethod
    @docval({'name': 'spec', 'type': Spec, 'doc': 'the specification to get the object attribute names for'})
    def get_attr_names(cls, **kwargs):
        '''Get the attribute names for each subspecification in a Spec'''
        spec = getargs('spec', kwargs)
        names = OrderedDict()
        for subspec in spec.attributes:
            cls.__get_fields(list(), names, subspec)
        if isinstance(spec, GroupSpec):
            for subspec in spec.groups:
                cls.__get_fields(list(), names, subspec)
            for subspec in spec.datasets:
                cls.__get_fields(list(), names, subspec)
            for subspec in spec.links:
                cls.__get_fields(list(), names, subspec)
        return names

    def __map_spec(self, spec):
        attr_names = self.get_attr_names(spec)
        for k, v in attr_names.items():
            self.map_spec(k, v)

    @docval({"name": "attr_name", "type": str, "doc": "the name of the object to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_attr(self, **kwargs):
        """ Map an attribute to spec. Use this to override default behavior """
        attr_name, spec = getargs('attr_name', 'spec', kwargs)
        if hasattr(spec, 'name') and spec.name is not None:
            n = spec.name
        elif hasattr(spec, 'data_type_def') and spec.data_type_def is not None:
            n = spec.data_type_def  # noqa: F841
        if attr_name in self.__attr2spec:
            existing = self.__attr2spec.pop(attr_name)
            if existing is not spec:
                self.__spec2attr.pop(existing)
        self.__spec2attr[spec] = attr_name
        self.__attr2spec[attr_name] = spec

    @docval({"name": "attr_name", "type": str, "doc": "the name of the attribute"})
    def get_attr_spec(self, **kwargs):
        """ Return the Spec for a given attribute """
        attr_name = getargs('attr_name', kwargs)
        return self.__attr2spec.get(attr_name)

    @docval({"name": "carg_name", "type": str, "doc": "the name of the constructor argument"})
    def get_carg_spec(self, **kwargs):
        """ Return the Spec for a given constructor argument """
        carg_name = getargs('carg_name', kwargs)
        return self.__attr2spec.get(carg_name)

    @docval({"name": "const_arg", "type": str, "doc": "the name of the constructor argument to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_const_arg(self, **kwargs):
        """ Map an attribute to spec. Use this to override default behavior """
        const_arg, spec = getargs('const_arg', 'spec', kwargs)
        if const_arg in self.__carg2spec:
            existing = self.__carg2spec.pop(const_arg)
            if existing is not spec:
                self.__spec2carg.pop(existing)
        self.__spec2carg[spec] = const_arg
        self.__carg2spec[const_arg] = spec

    @docval({"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def unmap(self, **kwargs):
        """ Removing any mapping for a specification. Use this to override default mapping """
        spec = getargs('spec', kwargs)
        self.__spec2attr.pop(spec, None)
        self.__spec2carg.pop(spec, None)

    @docval({"name": "attr_carg", "type": str, "doc": "the constructor argument/object attribute to map this spec to"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_spec(self, **kwargs):
        """ Map the given specification to the construct argument and object attribute """
        spec, attr_carg = getargs('spec', 'attr_carg', kwargs)
        self.map_const_arg(attr_carg, spec)
        self.map_attr(attr_carg, spec)

    def __get_override_carg(self, *args):
        name = args[0]
        remaining_args = tuple(args[1:])
        if name in self.constructor_args:
            func = self.constructor_args[name]
            try:
                # remaining_args is [builder, manager]
                return func(self, *remaining_args)
            except TypeError:
                # LEGACY: remaining_args is [manager]
                return func(self, *remaining_args[:-1])
        return None

    def __get_override_attr(self, name, container, manager):
        if name in self.obj_attrs:
            func = self.obj_attrs[name]
            return func(self, container, manager)
        return None

    @docval({"name": "spec", "type": Spec, "doc": "the spec to get the attribute for"},
            returns='the attribute name', rtype=str)
    def get_attribute(self, **kwargs):
        ''' Get the object attribute name for the given Spec '''
        spec = getargs('spec', kwargs)
        val = self.__spec2attr.get(spec, None)
        return val

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
                    ret = list(map(str, value))
                else:
                    ret = str(value)
        elif isinstance(spec, DatasetSpec):
            # TODO: make sure we can handle specs with data_type_inc set
            if spec.data_type_inc is not None:
                ret = value
            else:
                if 'text' in spec.dtype:
                    if spec.dims is not None:
                        ret = list(map(str, value))
                    else:
                        ret = str(value)
        return ret

    @classmethod
    def convert_dtype(self, dtype_spec):
        ret = dtype_spec
        if isinstance(dtype_spec, RefSpec):
            ret = dtype_spec.reftype
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
            {"name": "source", "type": str,
             "doc": "the source of container being built i.e. file path", 'default': None},
            returns="the Builder representing the given Container", rtype=Builder)
    def build(self, **kwargs):
        ''' Convert an Container to a Builder representation '''
        container, manager, parent, source = getargs('container', 'manager', 'parent', 'source', kwargs)
        name = manager.get_builder_name(container)
        if isinstance(self.__spec, GroupSpec):
            builder = GroupBuilder(name, parent=parent, source=source)
            self.__add_datasets(builder, self.__spec.datasets, container, manager, source)
            self.__add_groups(builder, self.__spec.groups, container, manager, source)
            self.__add_links(builder, self.__spec.links, container, manager, source)
        else:
            if not isinstance(container, Data):
                msg = "'container' must be of type Data with DatasetSpec"
                raise ValueError(msg)
            if isinstance(self.spec.dtype, RefSpec) and self.spec.dtype.is_region():
                if not isinstance(container, DataRegion):
                    msg = "'container' must be of type DataRegion if spec represents region reference"
                    raise ValueError(msg)
                builder = RegionBuilder(name, container.region, manager.build(container.data))
            else:
                builder = DatasetBuilder(name, data=container.data, parent=parent,
                                         dtype=self.convert_dtype(self.__spec.dtype), source=source)
        self.__add_attributes(builder, self.__spec.attributes, container)
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
            if spec.value is not None:
                attr_value = spec.value
            else:
                attr_value = self.get_attr_value(spec, container)
                if attr_value is None:
                    attr_value = spec.default_value

            if attr_value is None:
                if spec.required:
                    warnings.warn("missing required attribute '%s' for '%s' of type '%s'"
                                  % (spec.name, builder.name, self.spec.data_type_def))
                continue
            builder.set_attribute(spec.name, attr_value)

    def __add_links(self, builder, links, container, build_manager, source):
        for spec in links:
            attr_value = self.get_attr_value(spec, container)
            if not attr_value:
                continue
            self.__add_containers(builder, spec, attr_value, build_manager, source)

    def __add_datasets(self, builder, datasets, container, build_manager, source):
        for spec in datasets:
            attr_value = self.get_attr_value(spec, container)
            # TODO: add check for required datasets
            if attr_value is None:
                if spec.required:
                    warnings.warn("missing required attribute '%s' for '%s'" % (spec.name, builder.name))
                continue
            if spec.data_type_def is None and spec.data_type_inc is None:
                sub_builder = builder.add_dataset(spec.name, attr_value, dtype=self.convert_dtype(spec.dtype))
                self.__add_attributes(sub_builder, spec.attributes, container)
            else:
                self.__add_containers(builder, spec, attr_value, build_manager, source)

    def __add_groups(self, builder, groups, container, build_manager, source):
        for spec in groups:
            if spec.data_type_def is None and spec.data_type_inc is None:
                # we don't need to get attr_name since any named
                # group does not have the concept of value
                sub_builder = GroupBuilder(spec.name)
                self.__add_attributes(sub_builder, spec.attributes, container)
                self.__add_datasets(sub_builder, spec.datasets, container, build_manager, source)

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
                                self.__add_containers(sub_builder, spec, item, build_manager, source)
                self.__add_groups(sub_builder, spec.groups, container, build_manager, source)
                empty = sub_builder.is_empty()
                if not empty or (empty and isinstance(spec.quantity, int)):
                    builder.set_group(sub_builder)
            else:
                if spec.data_type_def is not None:
                    attr_name = self.get_attribute(spec)
                    if attr_name is not None:
                        attr_value = getattr(container, attr_name, None)
                        if attr_value is not None:
                            self.__add_containers(builder, spec, attr_value, build_manager, source)
                else:
                    attr_name = self.get_attribute(spec)
                    attr_value = getattr(container, attr_name, None)
                    if attr_value is not None:
                        self.__add_containers(builder, spec, attr_value, build_manager, source)

    def __add_containers(self, builder, spec, value, build_manager, source):
        if isinstance(value, Container):
            rendered_obj = build_manager.build(value, source=source)
            # use spec to determine what kind of HDF5
            # object this Container corresponds to
            if isinstance(spec, LinkSpec):
                name = spec.name
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
                self.__add_containers(builder, spec, container, build_manager, source)

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
                link_name = None
                if isinstance(sub_builder, LinkBuilder):
                    link_name = sub_builder.name  # noqa: F841
                subspec = manager.get_subspec(spec, sub_builder)
                if subspec is not None:
                    if isinstance(subspec, LinkSpec):
                        if isinstance(sub_builder, LinkBuilder):
                            sub_builder = sub_builder.builder
                        else:
                            # LEGACY
                            msg = 'expected LinkBuilder, got %s' % type(sub_builder).__name__
                            warnings.warn(msg)
                            continue
                    if self.__data_type_key in sub_builder.attributes or \
                       not (subspec.data_type_inc is None and subspec.data_type_def is None):
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

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder),
             'doc': 'the builder to construct the Container from'},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager for this build'})
    def construct(self, **kwargs):
        ''' Construct an Container from the given Builder '''
        builder, manager = getargs('builder', 'manager', kwargs)
        cls = manager.get_cls(builder)
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
            override = self.__get_override_carg(argname, builder, manager)
            if override is not None:
                val = override
            elif argname in const_args:
                val = const_args[argname]
            else:
                continue
            if 'default' in const_arg:
                kwargs[argname] = val
            else:
                args.append(val)
        try:
            obj = cls(*args, **kwargs)
        except Exception as ex:
            details = '%s: %s (%s)' % (ex, cls.__name__, builder.name)
            msg = 'Could not construct %s object\n    %s' % (cls.__name__, details)
            raise_from(Exception(msg), ex)
        return obj

    @docval({'name': 'container', 'type': Container, 'doc': 'the Container to get the Builder name for'})
    def get_builder_name(self, **kwargs):
        '''Get the name of a Builder that represents a Container'''
        container = getargs('container', kwargs)
        if self.__spec.name not in (NAME_WILDCARD, None):
            ret = self.__spec.name
        else:
            if container.name is None:
                if self.__spec.default_name is not None:
                    ret = self.__spec.default_name
                else:
                    msg = 'Unable to determine name of container type %s' % self.__spec.data_type_def
                    raise ValueError(msg)
            else:
                ret = container.name
        return ret


class TypeSource(object):
    '''A class to indicate the source of a data_type in a namespace.

    This class should only be used by TypeMap
    '''

    @docval({"name": "namespace", "type": str, "doc": "the namespace the from, which the data_type originated"},
            {"name": "data_type", "type": str, "doc": "the name of the type"})
    def __init__(self, **kwargs):
        namespace, data_type = getargs('namespace', 'data_type', kwargs)
        self.__namespace = namespace
        self.__data_type = data_type

    @property
    def namespace(self):
        return self.__namespace

    @property
    def data_type(self):
        return self.__data_type


class TypeMap(object):
    ''' A class to maintain the map between ObjectMappers and Container classes
    '''

    @docval({'name': 'namespaces', 'type': NamespaceCatalog, 'doc': 'the NamespaceCatalog to use'},
            {'name': 'mapper_cls', 'type': type, 'doc': 'the ObjectMapper class to use', 'default': ObjectMapper})
    def __init__(self, **kwargs):
        namespaces = getargs('namespaces', kwargs)
        self.__ns_catalog = namespaces
        self.__mappers = dict()     # already constructed ObjectMapper classes
        self.__mapper_cls = dict()  # the ObjectMapper class to use for each container type
        self.__container_types = dict()
        self.__data_types = dict()
        self.__default_mapper_cls = getargs('mapper_cls', kwargs)

    def __copy__(self):
        ret = TypeMap(self.__ns_catalog, self.__default_mapper_cls)
        ret.merge(self)
        return ret

    def __deepcopy__(self, memo):
        # XXX: From @nicain: All of a sudden legacy tests started
        #      needing this argument in deepcopy. Doesn't hurt anything, though.
        return self.__copy__()

    def merge(self, type_map):
        for namespace in type_map.__container_types:
            for data_type in type_map.__container_types[namespace]:
                container_cls = type_map.__container_types[namespace][data_type]
                self.register_container_type(namespace, data_type, container_cls)
        for container_cls in type_map.__mapper_cls:
            self.register_map(container_cls, type_map.__mapper_cls[container_cls])

    @docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the file containing the namespaces(s) to load'},
            {'name': 'resolve', 'type': bool,
             'doc': 'whether or not to include objects from included/parent spec objects', 'default': True},
            returns="the namespaces loaded from the given file", rtype=tuple)
    def load_namespaces(self, **kwargs):
        '''Load namespaces from a namespace file.

        This method will call load_namespaces on the NamespaceCatalog used to construct this TypeMap. Additionally,
        it will process the return value to keep track of what types were included in the loaded namespaces. Calling
        load_namespaces here has the advantage of being able to keep track of type dependencies across namespaces.
        '''
        namespace_path, resolve = getargs('namespace_path', 'resolve', kwargs)
        deps = self.__ns_catalog.load_namespaces(namespace_path, resolve)
        for new_ns, ns_deps in deps.items():
            for src_ns, types in ns_deps.items():
                for dt in types:
                    container_cls = self.get_container_cls(src_ns, dt)
                    if container_cls is None:
                        container_cls = TypeSource(src_ns, dt)
                    self.register_container_type(new_ns, dt, container_cls)
        return tuple(deps.keys())

    _type_map = {
        'text': str,
        'float': float,
        'float64': float,
        'int': int,
        'int32': int
    }

    @classmethod
    def __get_type(self, spec):
        if isinstance(spec, AttributeSpec):
            return self._type_map.get(spec.dtype)
        elif isinstance(spec, LinkSpec):
            return Container
        else:
            if not (spec.data_type_inc is None and spec.data_type_inc is None):
                if spec.name is not None:
                    return (list, tuple, dict, set)
                else:
                    return Container
            else:
                return (list, tuple, dict, set)

    @classmethod
    def __get_constructor(self, base, addl_fields):
        # TODO: fix this to be more maintainable and smarter
        existing_args = set()
        docval_args = list()
        new_args = list()
        if base is not None:
            for arg in get_docval(base.__init__):
                existing_args.add(arg['name'])
                if arg['name'] in addl_fields:
                    continue
                docval_args.append(arg)
        for f, field_spec in addl_fields.items():
            dtype = self.__get_type(field_spec)
            docval_arg = {'name': f, 'type': dtype, 'doc': field_spec.doc}
            if not field_spec.required:
                docval_arg['default'] = getattr(field_spec, 'default_value', None)
            docval_args.append(docval_arg)
            if f not in existing_args:
                new_args.append(f)
        # TODO: set __nwbfields__
        if base is None:
            @docval(*docval_args)
            def __init__(self, **kwargs):
                for f in new_args:
                    setattr(self, f, kwargs.get(f, None))
            return __init__
        else:
            @docval(*docval_args)
            def __init__(self, **kwargs):
                pargs, pkwargs = fmt_docval_args(base.__init__, kwargs)
                super(type(self), self).__init__(*pargs, **pkwargs)
                for f in new_args:
                    setattr(self, f, kwargs.get(f, None))
            return __init__

    @docval({"name": "namespace", "type": str, "doc": "the namespace containing the data_type"},
            {"name": "data_type", "type": str, "doc": "the data type to create a Container class for"},
            returns='the class for the given namespace and data_type', rtype=type)
    def get_container_cls(self, **kwargs):
        '''Get the container class from data type specification

        If no class has been associated with the ``data_type`` from ``namespace``,
        a class will be dynamically created and returned.
        '''
        namespace, data_type = getargs('namespace', 'data_type', kwargs)
        cls = self.__get_container_cls(namespace, data_type)
        if cls is None:
            dt_hier = self.__ns_catalog.get_hierarchy(namespace, data_type)
            parent_cls = None
            for t in dt_hier:
                parent_cls = self.__get_container_cls(namespace, t)
                if parent_cls is not None:
                    break
            bases = tuple()
            if parent_cls is not None:
                bases = (parent_cls,)
            name = data_type
            spec = self.__ns_catalog.get_spec(namespace, data_type)
            attr_names = self.__default_mapper_cls.get_attr_names(spec)
            fields = dict()
            for k, field_spec in attr_names.items():
                if not spec.is_inherited_spec(field_spec):
                    # fields.append(k)
                    fields[k] = field_spec
            d = {'__init__': self.__get_constructor(parent_cls, fields)}
            cls = type(name, bases, d)
            self.register_container_type(namespace, data_type, cls)
        return cls

    def __get_container_cls(self, namespace, data_type):
        if namespace not in self.__container_types:
            return None
        if data_type not in self.__container_types[namespace]:
            return None
        ret = self.__container_types[namespace][data_type]
        if isinstance(ret, TypeSource):
            # ret = self.__container_types[ret.namespace][ret.data_type]
            # self.register_container_type(namespace, data_type, ret)
            ret = self.__get_container_cls(ret.namespace, ret.data_type)
            if ret is not None:
                self.register_container_type(namespace, data_type, ret)
        return ret

    def get_builder_dt(self, builder):
        ret = builder.attributes.get(self.__ns_catalog.group_spec_cls.type_key())
        if ret is None:
            msg = "builder '%s' does not have a data_type" % builder.name
            raise ValueError(msg)

        if isinstance(ret, bytes):
            ret = ret.decode('UTF-8')

        return ret

    def get_builder_ns(self, builder):
        ret = builder.attributes.get('namespace')
        if ret is None:
            msg = "builder '%s' does not have a namespace" % builder.name
            raise ValueError(msg)
        return ret

    @docval({'name': 'builder', 'type': Builder,
             'doc': 'the Builder object to get the corresponding Container class for'})
    def get_cls(self, **kwargs):
        ''' Get the class object for the given Builder '''
        builder = getargs('builder', kwargs)
        data_type = self.get_builder_dt(builder)
        namespace = self.get_builder_ns(builder)
        return self.get_container_cls(namespace, data_type)

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'the parent spec to search'},
            {'name': 'builder', 'type': (DatasetBuilder, GroupBuilder, LinkBuilder),
             'doc': 'the builder to get the sub-specification for'})
    def get_subspec(self, **kwargs):
        '''
        Get the specification from this spec that corresponds to the given builder
        '''
        spec, builder = getargs('spec', 'builder', kwargs)
        if isinstance(builder, LinkBuilder):
            builder_type = type(builder.builder)
        else:
            builder_type = type(builder)
        if issubclass(builder_type, DatasetBuilder):
            subspec = spec.get_dataset(builder.name)
        else:
            subspec = spec.get_group(builder.name)
        if subspec is None:
            # builder was generated from something with a data_type and a wildcard name
            if isinstance(builder, LinkBuilder):
                dt = self.get_builder_dt(builder.builder)
            else:
                dt = self.get_builder_dt(builder)
            if dt is not None:
                # TODO: this returns None when using subclasses
                ns = self.get_builder_ns(builder)
                hierarchy = self.__ns_catalog.get_hierarchy(ns, dt)
                for t in hierarchy:
                    subspec = spec.get_data_type(t)
                    if subspec is not None:
                        break
        return subspec

    def __get_container_ns_dt(self, obj):
        container_cls = obj.__class__
        namespace, data_type = self.__get_container_cls_dt(container_cls)
        return namespace, data_type

    def __get_container_cls_dt(self, cls):
        return self.__data_types.get(cls, (None, None))

    @docval({'name': 'namespace', 'type': str,
             'doc': 'the namespace to get the container classes for', 'default': None})
    def get_container_classes(self, **kwargs):
        namespace = getargs('namespace', kwargs)
        ret = self.__data_types.keys()
        if namespace is not None:
            ret = filter(lambda x: self.__data_types[x][0] == namespace, ret)
        return list(ret)

    @docval({'name': 'obj', 'type': (Container, Builder), 'doc': 'the object to get the ObjectMapper for'},
            returns='the ObjectMapper to use for mapping the given object', rtype='ObjectMapper')
    def get_map(self, **kwargs):
        """ Return the ObjectMapper object that should be used for the given container """
        obj = getargs('obj', kwargs)
        # get the container class, and namespace/data_type
        if isinstance(obj, Container):
            container_cls = obj.__class__
            namespace, data_type = self.__get_container_ns_dt(obj)
            if namespace is None:
                raise ValueError("class %s does not mapped to a data_type" % container_cls)
        else:
            data_type = self.get_builder_dt(obj)
            namespace = self.get_builder_ns(obj)
            container_cls = self.get_cls(obj)
        # now build the ObjectMapper class
        spec = self.__ns_catalog.get_spec(namespace, data_type)
        mapper = self.__mappers.get(container_cls)
        if mapper is None:
            mapper_cls = self.__default_mapper_cls
            for cls in container_cls.type_hierarchy():
                tmp_mapper_cls = self.__mapper_cls.get(cls)
                if tmp_mapper_cls is not None:
                    mapper_cls = tmp_mapper_cls
                    break

            mapper = mapper_cls(spec)
            self.__mappers[container_cls] = mapper
        return mapper

    @docval({"name": "namespace", "type": str, "doc": "the namespace containing the data_type to map the class to"},
            {"name": "data_type", "type": str, "doc": "the data_type to mape the class to"},
            {"name": "container_cls", "type": (TypeSource, type), "doc": "the class to map to the specified data_type"})
    def register_container_type(self, **kwargs):
        ''' Map a container class to a data_type '''
        namespace, data_type, container_cls = getargs('namespace', 'data_type', 'container_cls', kwargs)
        self.__container_types.setdefault(namespace, dict())
        self.__container_types[namespace][data_type] = container_cls
        self.__data_types.setdefault(container_cls, (namespace, data_type))

    @docval({"name": "container_cls", "type": type,
             "doc": "the Container class for which the given ObjectMapper class gets used for"},
            {"name": "mapper_cls", "type": type, "doc": "the ObjectMapper class to use to map"})
    def register_map(self, **kwargs):
        ''' Map a container class to an ObjectMapper class '''
        container_cls, mapper_cls = getargs('container_cls', 'mapper_cls', kwargs)
        if self.__get_container_cls_dt(container_cls) == (None, None):
            raise ValueError('cannot register map for type %s - no data_type found' % container_cls)
        self.__mapper_cls[container_cls] = mapper_cls

    @docval({"name": "container", "type": Container, "doc": "the container to convert to a Builder"},
            {"name": "manager", "type": BuildManager,
             "doc": "the BuildManager to use for managing this build", 'default': None},
            {"name": "source", "type": str,
             "doc": "the source of container being built i.e. file path", 'default': None})
    def build(self, **kwargs):
        """ Build the GroupBuilder for the given Container"""
        container, manager = getargs('container', 'manager', kwargs)
        if manager is None:
            manager = BuildManager(self)
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for container of type %s' % str(container.__class__.__name__))
        else:
            builder = attr_map.build(container, manager, source=getargs('source', kwargs))
        namespace, data_type = self.__get_container_ns_dt(container)
        builder.set_attribute('namespace', namespace)
        builder.set_attribute(attr_map.spec.type_key(), data_type)
        return builder

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder),
             'doc': 'the builder to construct the Container from'},
            {'name': 'build_manager', 'type': BuildManager,
             'doc': 'the BuildManager for constructing', 'default': None})
    def construct(self, **kwargs):
        """ Construct the Container represented by the given builder """
        builder, build_manager = getargs('builder', 'build_manager', kwargs)
        if build_manager is None:
            build_manager = BuildManager(self)
        attr_map = self.get_map(builder)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for builder of type %s'
                             % str(container.__class__.__name__))  # noqa: F821
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
