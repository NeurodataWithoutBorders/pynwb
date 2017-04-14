from pynwb.core import docval, getargs, ExtenderMeta, NWBContainer, get_docval
from pynwb.spec import Spec, DatasetSpec, GroupSpec, LinkSpec, NAME_WILDCARD
from pynwb.spec.spec import SpecCatalog
from .builders import DatasetBuilder, GroupBuilder, LinkBuilder, Builder
import sys

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

class TypeMap(object):

    @docval({'name': 'catalog', 'type': SpecCatalog, 'doc': 'a catalog of existing specifications'})
    def __init__(self, **kwargs):
        catalog = getargs('catalog', kwargs)
        self.__maps = dict()
        self.__map_types = dict()
        self.__catalog = catalog
        self.__classes = self.__get_subclasses(NWBContainer)

    def __get_subclasses(self, cls):
        ret = dict()
        for subcls in cls.__subclasses__():
            ret[subcls.__name__] = subcls
            ret.update(self.__get_subclasses(subcls))
        return ret

    def get_cls(self, cls_name):
        return self.__classes.get(cls_name)


    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            {'name': 'spec', 'type': Spec, 'doc': 'a Spec object'})
    def register_spec(self, **kwargs):
        """
        Specify the specification for an NWBContainer type
        """
        obj_type, spec = getargs('obj_type', 'spec', kwargs)
        ndt = spec.neurodata_type_def
        if ndt is None:
            raise ValueError("'spec' must define a neurodata type")
        self.__catalog.register_spec(obj_type, spec)

    @docval({'name': 'spec', 'type': Spec, 'doc': 'the Spec object to register'})
    def auto_register(self, **kwargs):
        '''
        Register this specification and all sub-specification using neurodata_type as object type name
        '''
        spec = getargs('spec', kwargs)
        ndt = spec.neurodata_type_def
        if ndt is not None:
            self.register_spec(ndt, spec)
        for dataset_spec in spec.datasets:
            dset_ndt = dataset_spec.neurodata_type_def
            if dset_ndt is not None:
                self.register_spec(dset_ndt, dataset_spec)
        for group_spec in spec.groups:
            self.auto_register(group_spec)

    @docval({'name': 'ndt', 'type': (type, str), 'doc': 'the neurodata type to associate the decorated class with'})
    def neurodata_type(self, **kwargs):
        """
        A decorator to specify ObjectMapper subclasses for specific neurodata types
        """
        ndt = getargs('ndt', kwargs)
        def _dec(map_cls):
            self.__map_types[ndt] = map_cls
            return map_cls
        return _dec

    def get_map(self, obj):
        """
        Return the ObjectMapper object that should be used for the given container
        """
        if isinstance(obj, NWBContainer):
            ndt = obj.__class__.__name__
        elif isinstance(obj, GroupBuilder) or isinstance(obj, DatasetBuilder):
            ndt = obj.attributes.get('neurodata_type')
        spec = self.__catalog.get_spec(ndt)
        map_cls = self.__map_types.get(ndt, ObjectMapper)
        return map_cls(spec)

    def get_registered_types(self):
        """
        Return all NWBContainer types that have a map specified
        """
        return tuple(self.__maps.keys())

    def build(self, container, build_manager=None):
        """
        Build the GroupBuilder for the given NWBContainer
        """
        if build_manager is None:
            build_manager = BuildManager()
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.build(container, build_manager)

    def construct(self, builder, build_manager=None):
        """
        Construct the NWBContainer represented by the given builder
        """
        if build_manager is None:
            build_manager = BuildManager()
        attr_map = self.get_map(builder)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for builder of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.construct(builder, build_manager)

    def get_builder_name(self, container):
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No ObjectMapper found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.get_builder_name(container)

class BuildManager(object):
    """
    A class for managing builds of NWBContainers
    """

    def __init__(self, type_map):
        self.__builders = dict()
        self.__containers = dict()
        self.__type_map = type_map

    def build(self, container):
        container_id = self.__conthash__(container)
        result = self.__builders.setdefault(container_id, self.__type_map.build(container, self))
        self.prebuilt(container, result)
        return result

    def prebuilt(self, container, builder):
        container_id = self.__conthash__(container)
        self.__builders[container_id] = builder
        builder_id = self.__bldrhash__(builder)
        self.__containers[builder_id] = container

    def __conthash__(self, obj):
        return id(obj)

    def __bldrhash__(self, obj):
        return id(obj)

    def construct(self, builder):
        if isinstance(builder, LinkBuilder):
            builder = bulder.target
        builder_id = self.__bldrhash__(builder)
        result = self.__containers.get(builder_id)
        if result is None:
            result = self.__type_map.construct(builder, self)
            self.__containers[builder_id] = result
        return result

    def get_cls(self, builder):
        return self.__type_map.get_cls(builder.attributes.get('neurodata_type'))

    def get_builder_name(self, container):
        return self.__type_map.get_builder_name(container)


class ObjectMapper(object, metaclass=ExtenderMeta):

    __const_arg = '__const_arg__'
    @classmethod
    def const_arg(cls, name):
        def _dec(func):
            setattr(func, cls.__const_arg, name)
            return func
        return _dec

    @classmethod
    def __is_const_arg(cls, attr_val):
        return hasattr(attr_val, cls.__const_arg)

    @classmethod
    def __get_cargname(cls, attr_val):
        return getattr(attr_val, cls.__const_arg)

    _property = "__item_property__"
    @ExtenderMeta.post_init
    def __gather_procedures(cls, name, bases, classdict):
        cls.const_args = dict()
        for name, func in filter(lambda tup: cls.__is_const_arg(tup[1]), cls.__dict__.items()):
            cls.const_args[cls.__get_cargname(func)] = getattr(cls, name)

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications
        """
        spec = getargs('spec', kwargs)
        self.__spec = spec
        self.__spec2attr = dict()
        self.__spec2carg = dict()
        for subspec in spec.attributes:
            self.__map_spec(subspec)
        if isinstance(spec, GroupSpec):
            for subspec in spec.datasets:
                self.__map_spec(subspec)
            for subspec in spec.groups:
                self.__map_spec(subspec)

    def __map_spec(self, spec):
        if spec.name != NAME_WILDCARD:
            self.map_attr(spec.name, spec)
            self.map_const_arg(spec.name, spec)
        else:
            self.__spec2attr[subspec] = subspec.neurodata_type
            self.__spec2attr[subspec] = subspec.neurodata_type
        if isinstance(spec, DatasetSpec):
            for subspec in spec.attributes:
                self.__map_spec(subspec)

    def __get_override_carg(self, name, builder):
        if name in self.const_args:
            func = getattr(self, self.const_args[name])
            return func(builder)
        return None

    @property
    def spec(self):
        return self.__spec

    def get_attribute(self, spec):
        '''
        Get the object attribute name for the given Spec
        '''
        return self.__spec2attr.get(spec, None)

    def get_const_arg(self, spec):
        '''
        Get the constructor argument for the given Spec
        '''
        #if spec not in self.__spec2carg:
        #    print("spec == %s" % str(spec), file=sys.stderr)
        return self.__spec2carg.get(spec, None)

    def build(self, container, build_manager, parent=None):
        name = build_manager.get_builder_name(container)
        if isinstance(self.__spec, GroupSpec):
            builder = GroupBuilder(name, parent=parent)
            self.__add_datasets(builder, self.__spec.datasets, container, build_manager)
            self.__add_groups(builder, self.__spec.groups, container, build_manager)
        else:
            builder = DatasetBuilder(name, parent=parent)
        self.__add_attributes(builder, self.__spec.attributes, container)
        return builder

    def __add_attributes(self, builder, attributes, container):
        for spec in attributes:
            attr_name = self.get_attribute(spec)
            attr_value = getattr(container, attr_name)
            if attr_value is None:
                continue
            builder.set_attribute(spec.name, attr_value)

    def __add_datasets(self, builder, datasets, container, build_manager):
        for spec in datasets:
            attr_name = self.get_attribute(spec)
            attr_value = getattr(container, attr_name)
            if attr_value is None:
                continue
            if spec.neurodata_type is None:
                sub_builder = builder.add_dataset(spec.name, attr_value)
                self.__add_attributes(sub_builder, spec.attributes, container)
            else:
                self.__build_helper(builder, spec, attr_value, build_manager)

    def __add_groups(self, builder, groups, container, build_manager):
        for spec in groups:
            if spec.neurodata_type is None:
                # we don't need to get attr_name since any named
                # group does not have the concept of value
                sub_builder = builder.add_group(spec.name)
                self.__add_attributes(sub_builder, spec.attributes, container)
                self.__add_datasets(sub_builder, spec.datasets, container, build_manager)
                self.__add_groups(sub_builder, spec.groups, container, build_manager)
            else:
                attr_name = self.get_attribute(spec)
                value = getattr(container, attr_name)
                self.__build_helper(builder, spec, value, build_manager)

    def __build_helper(self, builder, spec, value, build_manager):
        if isinstance(value, NWBContainer):
            rendered_obj = build_manager.build(value)
            name = build_manager.get_builder_name(value)
            # use spec to determine what kind of HDF5
            # object this NWBContainer corresponds to
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
                msg = ("received %s, expected NWBContainer - 'value' "
                       "must be an NWBContainer a list/tuple/dict of "
                       "NWBContainers if 'spec' is a GroupSpec")
                raise ValueError(msg % value.__class__.__name__)
            for container in values:
                self.__build_helper(builder, spec, container, build_manager)

    @docval({"name": "attr_name", "type": str, "doc": "the name of the object to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_attr(self, **kwargs):
        """Map an attribute to spec. Use this to override default
           behavior
        """
        attr_name, spec = getargs('attr_name', 'spec', kwargs)
        self.__spec2attr[spec] = attr_name

    @docval({"name": "const_arg", "type": str, "doc": "the name of the constructor argument to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_const_arg(self, **kwargs):
        """Map an attribute to spec. Use this to override default
           behavior
        """
        const_arg, spec = getargs('const_arg', 'spec', kwargs)
        self.__spec2carg[spec] = const_arg

    def __get_subspec_values(self, builder, spec, manager):
        ret = dict()
        for h5attr_name, h5attr_val in builder.attributes.items():
            subspec = spec.get_attribute(h5attr_name)
            if subspec is None:
                continue
            ret[subspec] = h5attr_val
            #print('iterattribs --> %s: %s' % (str(subspec), str(h5attr_val)))
        if isinstance(builder, GroupBuilder):
            for sub_builder_name, sub_builder in builder.items():
                if not isinstance(sub_builder, Builder):
                    continue
                subspec = get_subspec(self.spec, sub_builder)
                if subspec is not None:
                    if 'neurodata_type' in sub_builder.attributes:
                        ret[subspec] = build_manager.construct(sub_builder, manager)
                    else:
                        ret[subspec] = sub_builder
                        ret.update(self.__get_subspec_values(sub_builder, subspec, manager))
        else:
            ret[spec] = builder.data
        return ret

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the builder to construct the NWBContainer from'},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager for this build'})
    def construct(self, **kwargs):
        builder, manager = getargs('builder', 'manager', kwargs)
        cls = manager.get_cls(builder)
        # gather all subspecs
        subspecs = self.__get_subspec_values(builder, self.spec, manager)
        # get the constructor argument each specification corresponds to
        const_args = dict()
        #print('found these subspecs')
        for subspec, value in subspecs.items():
            #print('%s: %s' % (str(subspec), str(value)))
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
