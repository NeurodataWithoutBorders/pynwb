from pynwb.core import docval, getargs
from pynwb.io.spec import BaseStorageSpec, Spec

class TypeMap(object):
    __maps = dict()

    __map_types = dict()

    __built = dict()

    @classmethod
    def register_map(cls, container_type, attr_map):
        """
        Specify the attribute map for an NWBContainer type
        """
        cls.__maps[container_type.__name__] = attr_map

    @classmethod
    def register_spec(cls, container_type, spec):
        """
        Specify the specification for an NWBContainer type
        """
        SpecCatalog.register_spec(container_type, spec)
        ndt = spec.neurodata_type_def
        if ndt is None:
            raise ValueError("'spec' must define a neurodata type")
        map_cls = cls.__map_types.get(ndt, H5Builder)
        cls.register_map(container_type, map_cls(spec))

    @classmethod
    def neurodata_type(cls, ndt):
        """
        A decorator to specify H5Builder subclasses for specific neurodata types
        """
        def _dec(map_cls):
            cls.__map_types[ndt] = map_cls
            return map_cls
        return _dec

    @classmethod
    def get_map(cls, container):
        """
        Return the H5Builder object that should be used for the given container
        """
        cls.__maps.get(container.__class__.__name__, None)

    @classmethod
    def get_registered_types(cls):
        """
        Return all NWBContainer types that have a map specified
        """
        return tuple(cls.__maps.keys())

    @classmethod
    def build(cls, container, build_manager):
        """
        Build the GroupBuilder for the given NWBContainer
        """
        attr_map = cls.get_map(container)
        if attr_map is None:
            raise ValueError('No H5Builder found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.build(container, build_manager)

    @classmethod
    def get_h5object_name(cls, container):
        attr_map = cls.get_map(container)
        if attr_map is None:
            raise ValueError('No H5Builder found for container of type %s' % str(container.__class__.__name__))
        else:
            return attr_map.get_h5object_name(container)

class H5BuildManager(object):
    """
    A class for managing builds of NWBContainers
    """

    def __init__(self):
        self.__built = dict()

    def build(self, container):
        container_id = id(container)
        return self.__built.setdefault(id(container), TypeMap.build(container, self))

    def prebuilt(self, container, builder):
        self.__built[id(container)] = builder

class H5Builder(object):

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications
        """
        spec = getargs('spec', **kwargs)
        self.__spec = spec
        self.__attr_map = dict()
        self.__spec_map
        for spec in chain(spec.attributes, spec.datasets):
            if spec.name != '*':
                self.__attr_map[spec.name] = spec
                self.__spec_map[spec] = spec.name

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
        if isinstance(spec, DatasetSpec):
            builder = DatasetBuilder()
        else:
            builder = GroupBuilder()
        # keep track of which specs we've built something for
        seen = {self.spec: builder}

        attrs = deque(container.nwb_fields)
        while attrs:
            tmp_builder = builder
            attr_name = attrs.pop()
            attr_value = getattr(container, attr_name)
            attr_spec = self.get_spec(attr_name)
            if attr_spec is None:
                continue
            tmp_builder = seen.get(attr_spec.parent, None)
            if tmp_builder is not None:
                sub_builder = self.__build_helper(tmp_builder, attr_spec, attr_value, build_manager)
                if sub_builder is not None:
                    seen[attr_spec] = sub_builder
                #child_attributes.append(attr_name)
            else:
                attrs.appendleft(attr_name)

        return builder

    @docval({'name': 'builder', 'type': (DatasetBuilder, GroupBuilder), 'doc': 'the parent builder object to build on'},
            {'name': 'spec', 'type': Spec, 'doc': 'the specification to use for building'},
            {'name': 'value', 'type': None, 'doc': 'the value to add to builder using spec'},
            {'name': 'build_manager', 'type': H5BuildManager, 'doc': 'the manager for this build'})
    def __build_helper(self, **kwargs):
        builder, spec, value, build_manager = getargs('builder', 'spec', 'value', 'build_manager', kwargs)
        sub_builder = None
        if isinstance(value, NWBContainer):
            rendered_obj = build_manager.build(value)
            name = TypeMap.get_h5object_name(value)
            if isinstance(spec, LinkSpec):
                sub_builder = builder.add_link(name, rendered_obj)
            elif isinstance(spec, DatasetSpec):
                sub_builder = builder.add_dataset(name, rendered_obj)
            else:
                sub_builder = builder.add_group(name, rendered_obj)
        else:
            if isinstance(spec, AttributeSpec):
                builder.add_attribute(spec.name, value)
            elif isinstance(spec, DatasetSpec):
                sub_builder = builder.add_dataset(spec.name, value)
            elif isinstance(spec, GroupSpec):
                #TODO: this assumes that value is a NWBContainer or a list of NWBContainers
                # This is where spec.name comes from -- Containers have a name value
                group_name = spec.name
                if any(isinstance(value, t) for t in (list, tuple)):
                    values = value
                elif isinstance(value, dict):
                    values = value.values()
                else:
                    msg = ("received %s, expected NWBContainer - 'value' "
                           "must be an NWBContainer a list/tuple/dict of "
                           "NWBContainers if 'spec' is a GroupSpec")
                    raise ValueError(msg % value.__class__.__name__)
                for container in attrs:
                    self.__process_spec(builder, spec, container)
        return sub_builder


    @docval({"name": "attr_name", "type": str, "doc": "the name of the object to map"},
            {"name": "spec", "type": Spec, "doc": "the spec to map the attribute to"})
    def map_attr(self, **kwargs):
        """Map an attribute to spec. Use this to override default
           behavior
        """
        attr_name, spec = getargs()
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

    @staticmethod
    def determine_python_type(h5_object):
        name = h5_object.name
        if 'neurodata_type' in h5_object.attrs:
            neurodata_type = h5_object.attrs['']
            if neurodata_type == 'Interface' :
                return Interface.get_extensions(name.split('/')[-1])
            elif neurodata_type == 'TimeSeries' :
                return TimeSeries.get_extensions(h5_object.attrs['ancestry'][-1])
            elif neurodata_type == 'Module' :
                return Module
            elif neurodata_type == 'Epoch' :
                return Epoch
        else:
            if name.startswith('/general/extracellular_ephys'):
                return ElectrodeGroup
            elif name.startswith('/general/intracellular_ephys'):
                return IntracellularElectrode
            elif name.startswith('/general/optogenetics'):
                return OptogeneticSite
            elif name.startswith('/general/optophysiology'):
                name_ar = name[1:].split('/')
                if len(name_ar) == 3:
                    return ImagingPlane
                elif len(name_ar) == 4:
                    return OpticalChannel
        return None

@TypeMap.neurodata_type('TimeSeries')
class TimeSeriesMap(H5Builder):

    def __init__(self, spec):
        super(TimeSeriesMap, self).__init__(spec):
        data_spec = self.spec.get_dataset('data')
        self.map_attr('unit', data_spec.get_attribute('unit'))
        self.map_attr('resolution', data_spec.get_attribute('resolution'))
        self.map_attr('conversion', data_spec.get_attribute('conversion'))
        timestamps_spec = self.spec.get_dataset('timestamps')
        self.map_attr('timestamps_unit', timestamps_spec.get_attribute('unit'))
        self.map_attr('interval', timestamps_spec.get_attribute('interval'))
        startingtime_spec = self.spec.get_dataset('starting_time')
        self.map_attr('rate_unit', startingtime_spec.get_attribute('unit'))
        self.map_attr('rate', startingtime_spec.get_attribute('rate'))

class Condition(object):
    def __init__(self, key, value, spec_type=None, condition=None):
        self._key = key
        self._value = value
        self._condition = condition
        self_spec_type = spec_type

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def __str__(self):
        tmp = [("key", self._key),
               ("value", self._value)]
        if self._condition:
            tmp.append(('condition', str(self._condition)))
        return '{' + ", ".join(lambda x: '"%s": "%s"' % x, tmp) + '}'

    @property
    def condition(self):
        self._condition

    def find(self, spec):
        result = None
        if self._spec_type:
            for sub_spec in spec[self._spec_type]:
                if sub_spec[self._key] == self._value:
                    result = sub_spec
                    break
        if self._condition:
            result = self._condition.find(spec)
        return result

