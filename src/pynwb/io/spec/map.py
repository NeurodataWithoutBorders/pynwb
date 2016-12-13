
class TypeMap(object):
    __maps = dict()

    @classmethod
    def register_map(cls, container_type, attr_map):
        cls.__maps[container_type.__name__] = attr_map

    @classmethod
    def register_spec(cls, container_type, spec):
        SpecCatalog.register_spec(container_type, spec)
        cls.register_map(container_type, AttrMap(spec))

    @classmethod
    def get_map(cls, container):
        cls.__maps.get(container.__class__.__name__, None)

    def get_registered_types(cls):
        return tuple(cls.__maps.keys())

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
               ("value": self._value)]
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
        

class AttrMap(object):
    
    @docval({'name': 'spec', 'type': AttributableSpec, 'doc': 'The specification for mapping objects to builders'})
    def __init__(self, **kwargs):
        """ Create a map from Container attributes to NWB specifications
        """
        spec = getargs('spec', **kwargs)
        self._spec = spec
        self._attr_map = dict()
        self._spec_map
        for spec in chain(spec.attributes, spec.datasets):
            if spec.name != '*':
                self._attr_map[spec.name] = spec
                self._spec_map[spec] = spec.name

    @property
    def children(self):
        return self._attr_map

    @property
    def spec(self):
        return self._spec

    def get_attribute(self, spec):
        return self._attr_spec[spec]

    def get_spec(self, attr_name):
        return self._attr_map[attr_name]

    @docval({"name": "attr_name", "type": str, "doc": "The name of the object to map"},
            {"name": "spec", "type": (Condition, Spec), "doc": "The condition specifying the location within this map, or the spec"})
    def map_attr(self, attr_name, spec):
        """Map an attribute to spec. Use this to override default
           behavior
        """
        tmp = spec
        if isinstance(spec, Condition):
            tmp = spec.find(self._spec)
            if not tmp:
                raise KeyError(str(spec))
        self._attr_map[attr_name] = tmp
        self._spec_map[tmp] = attr_name

    def get_group_name(self, container):
        ret = container.name
        if self._spec.name != '*':
            ret = self._spec.name
        return ret
