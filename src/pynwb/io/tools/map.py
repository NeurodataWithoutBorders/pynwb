from itertools import chain

from pynwb.core import docval, getargs
from .spec import SpecCatalog, Spec, DatasetSpec, GroupSpec, LinkSpec
from .h5tools import DatasetBuilder, GroupBuilder

class TypeMap(object):

    @docval({'name': 'catalog', 'type': SpecCatalog, 'doc': 'a catalog of existing specifications'})
    def __init__(self, **kwargs):
        catalog = getargs('catalog', kwargs)
        self.__maps = dict()
        self.__map_types = dict()
        self.__catalog = catalog

    #@docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
    #        {'name': 'attr_map', 'type': 'H5Builder', 'doc': 'as H5Builder object'})
    #def register_map(self, **kwargs):
    #    """
    #    Specify the attribute map for an NWBContainer type
    #    """
    #    obj_type, attr_map = getargs('obj_type', 'attr_map', kwargs)
    #    type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
    #    self.__maps[type_name] = attr_map

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            {'name': 'spec', 'type': 'Spec', 'doc': 'a Spec object'})
    def register_spec(self, **kwargs):
        """
        Specify the specification for an NWBContainer type
        """
        obj_type, spec = getargs('obj_type', 'spec', kwargs)
        self.__catalog.register_spec(obj_type, spec)
        ndt = spec.neurodata_type_def
        if ndt is None:
            raise ValueError("'spec' must define a neurodata type")
        #self.register_map(obj_type, map_cls(spec))

    @docval({'name': 'spec', 'type': 'Spec', 'doc': 'the Spec object to register'})
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
        A decorator to specify H5Builder subclasses for specific neurodata types
        """
        ndt = getargs('ndt', kwargs)
        def _dec(map_cls):
            self.__map_types[ndt] = map_cls
            spec = self.__catalog.get_spec(ndt)
            #if spec is not None:
            #    self.register_map(ndt, map_cls(spec))
            return map_cls
        return _dec

    def get_map(self, container):
        """
        Return the H5Builder object that should be used for the given container
        """
        ndt = container.__class__.__name__
        spec = self.__catalog.get_spec(ndt)
        map_cls = self.__map_types.get(ndt, H5Builder)
        return map_cls(spec)
        #return self.__maps.get(container.__class__.__name__, None)

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
            raise ValueError('No H5Builder found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.build(container, build_manager)

    def get_h5object_name(self, container):
        attr_map = self.get_map(container)
        if attr_map is None:
            raise ValueError('No H5Builder found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.get_h5object_name(container)

class BuildManager(object):
    """
    A class for managing builds of NWBContainers
    """

    def __init__(self):
        self.__built = dict()

    def build(self, container):
        container_id = self.__ohash__(container)
        return self.__built.setdefault(container_id, TypeMap.build(container, self))

    def prebuilt(self, container, builder):
        self.__built[container_id] = builder

    def __ohash__(self, obj):
        return id(obj)

class H5Builder(object):

    @docval({'name': 'spec', 'type': (DatasetSpec, GroupSpec), 'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications
        """
        spec = getargs('spec', kwargs)
        self.__spec = spec
        self.__attr_map = dict()
        self.__spec_map = dict()
        self.__map_specs(spec)

    def __map_specs(self, spec):
        for subspec in chain(spec.attributes, spec.datasets):
            if subspec.name is not None:
                self.__attr_map[subspec.name] = subspec
                self.__spec_map[subspec] = subspec.name
            else:
                self.__attr_map[subspec.neurodata_type] = subspec
                self.__spec_map[subspec] = subspec.neurodata_type
        for subspec in spec.groups:
            self.__map_specs(subspec)

    @property
    def children(self):
        return self.__attr_map

    @property
    def spec(self):
        return self.__spec

    def get_attribute(self, spec):
        '''
        Get the object attribute name for the given Spec
        '''
        return self.__spec_map[spec]

    def get_spec(self, attr_name):
        '''
        Get the specification for the given object attribute name
        '''
        return self.__attr_map[attr_name]

    def build(self, container, build_manager):
        group = isinstance(self.__spec, GroupSpec)
        if group:
            builder = GroupBuilder()
            self.__add_datasets(builder, self.__spec.datasets, container, build_manager)
            self.__add_groups(builder, self.__spec.groups, container, build_manager)
        else:
            builder = DatasetBuilder()
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

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the parent builder object to build on'},
            {'name': 'spec', 'type': (DatasetSpec, GroupSpec, LinkSpec), 'doc': 'the specification to use for building'},
            {'name': 'value', 'type': None, 'doc': 'the value to add to builder using spec'},
            {'name': 'build_manager', 'type': BuildManager, 'doc': 'the manager for this build'})
    def __build_helper(self, **kwargs):
        builder, spec, value, build_manager = getargs('builder', 'spec', 'value', 'build_manager', kwargs)
        sub_builder = None
        if isinstance(value, NWBContainer):
            rendered_obj = build_manager.build(value)
            name = TypeMap.get_h5object_name(value)
            # use spec to determine what kind of HDF5
            # object this NWBContainer corresponds to
            if isinstance(spec, LinkSpec):
                sub_builder = builder.add_link(name, rendered_obj)
            elif isinstance(spec, DatasetSpec):
                sub_builder = builder.add_dataset(name, rendered_obj)
            else:
                sub_builder = builder.add_group(name, rendered_obj)
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
        return sub_builder

    @docval({"name": "attr_name", "type": str, "doc": "the name of the object to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_attr(self, **kwargs):
        """Map an attribute to spec. Use this to override default
           behavior
        """
        attr_name, spec = getargs('attr_name', 'spec', kwargs)
        tmp = spec
        self.__attr_map[attr_name] = tmp
        self.__spec_map[tmp] = attr_name

    def get_h5object_name(self, container):
        ret = container.name
        if self.__spec.name != '*':
            ret = self.__spec.name
        return ret

    @docval({"name": "attr_name", "type": str, "doc": "the name of the HDF5 attribute"},
            {"name": "attr_val", "type": None, "doc": "the value of the HDF5 attribute"})
    def get_attribute_h5attr(self, **kwargs):
        ''' Get the Python object attribute name and value given an HDF5 attribute name and value
        '''
        h5attr_name, h5attr_val = get_args('attr_name', 'attr_val', kwargs)
        attribute_name = self.get_attribute(self.__spec.get_attribute(h5attr_name))
        # do something to figure out the value of the attribute
        attribute_value = h5attr_val
        return attribute_name, attribute_value

    @docval({"name": "dset_name", "type": str, "doc": "the name of the HDF5 dataset"},
            {"name": "dset_val", "type": None, "doc": "the value of the HDF5 dataset"})
    def get_attribute_h5dataset(self, **kwargs):
        ''' Get the Python object attribute name and value given an HDF5 dataset name and value
        '''
        h5dset_name, h5dset_val = get_args('dset_name', 'dset_val', kwargs)
        attribute_name = self.get_attribute(self.__spec.get_dataset(h5dset_name))
        # do something to figure out the value of the attribute
        attribute_value = h5dset_val
        return attribute_name, attribute_value

    @docval({"name": "grp_name", "type": str, "doc": "the name of the HDF5 group"},
            {"name": "grp", "type": None, "doc": "the HDF5 group object"})
    def get_attribute_nwbcontainer(self, **kwargs):
        ''' Get the Python object attribute name and value given an HDF5 dataset name and value
        '''
        grp_name, grp = get_args('grp_name', 'grp', kwargs)
        pynwb_type = self.determine_python_type(grp)
        spec = TypeMap.get_spec(pynwb_type)

#    @staticmethod
#    def determine_python_type(h5_object):
#        name = h5_object.name
#        if 'neurodata_type' in h5_object.attrs:
#            neurodata_type = h5_object.attrs['']
#            if neurodata_type == 'Interface' :
#                return Interface.get_extensions(name.split('/')[-1])
#            elif neurodata_type == 'TimeSeries' :
#                return TimeSeries.get_extensions(h5_object.attrs['ancestry'][-1])
#            elif neurodata_type == 'Module' :
#                return Module
#            elif neurodata_type == 'Epoch' :
#                return Epoch
#        else:
#            if name.startswith('/general/extracellular_ephys'):
#                return ElectrodeGroup
#            elif name.startswith('/general/intracellular_ephys'):
#                return IntracellularElectrode
#            elif name.startswith('/general/optogenetics'):
#                return OptogeneticSite
#            elif name.startswith('/general/optophysiology'):
#                name_ar = name[1:].split('/')
#                if len(name_ar) == 3:
#                    return ImagingPlane
#                elif len(name_ar) == 4:
#                    return OpticalChannel
#        return None
#
#@pynwb.io.TypeMap.neurodata_type('TimeSeries')
#class TimeSeriesMap(H5Builder):
#
#    def __init__(self, spec):
#        super(TimeSeriesMap, self).__init__(spec)
#        data_spec = self.spec.get_dataset('data')
#        self.map_attr('unit', data_spec.get_attribute('unit'))
#        self.map_attr('resolution', data_spec.get_attribute('resolution'))
#        self.map_attr('conversion', data_spec.get_attribute('conversion'))
#        timestamps_spec = self.spec.get_dataset('timestamps')
#        self.map_attr('timestamps_unit', timestamps_spec.get_attribute('unit'))
#        self.map_attr('interval', timestamps_spec.get_attribute('interval'))
#        startingtime_spec = self.spec.get_dataset('starting_time')
#        self.map_attr('rate_unit', startingtime_spec.get_attribute('unit'))
#        self.map_attr('rate', startingtime_spec.get_attribute('rate'))
#
#class Condition(object):
#    def __init__(self, key, value, spec_type=None, condition=None):
#        self._key = key
#        self._value = value
#        self._condition = condition
#        self_spec_type = spec_type
#
#    @property
#    def key(self):
#        return self._key
#
#    @property
#    def value(self):
#        return self._value
#
#    def __str__(self):
#        tmp = [("key", self._key),
#               ("value", self._value)]
#        if self._condition:
#            tmp.append(('condition', str(self._condition)))
#        return '{' + ", ".join(lambda x: '"%s": "%s"' % x, tmp) + '}'
#
#    @property
#    def condition(self):
#        self._condition
#
#    def find(self, spec):
#        result = None
#        if self._spec_type:
#            for sub_spec in spec[self._spec_type]:
#                if sub_spec[self._key] == self._value:
#                    result = sub_spec
#                    break
#        if self._condition:
#            result = self._condition.find(spec)
#        return result
#
