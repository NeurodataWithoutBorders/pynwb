import abc
from datetime import datetime
from copy import deepcopy, copy
from ..utils import docval, getargs, popargs, get_docval

NAME_WILDCARD = None
ZERO_OR_ONE = '?'
ZERO_OR_MANY = '*'
ONE_OR_MANY = '+'
FLAGS = {
    'zero_or_one': ZERO_OR_ONE,
    'zero_or_many': ZERO_OR_MANY,
    'one_or_many': ONE_OR_MANY
}

class ConstructableDict(dict, metaclass=abc.ABCMeta):
    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this ConstructableDict class from a dictionary '''
        return deepcopy(spec_dict)

    @classmethod
    def build_spec(cls, spec_dict):
        ''' Build a Spec object from the given Spec dict '''
        kwargs = cls.build_const_args(spec_dict)
        try:
            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)

class Spec(ConstructableDict):
    ''' A base specification class
    '''

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
            {'name': 'name', 'type': str, 'doc': 'The name of this attribute', 'default': None},
            {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
            {'name': 'parent', 'type': 'Spec', 'doc': 'the parent of this spec', 'default': None})
    def __init__(self, **kwargs):
        name, doc, required, parent = getargs('name', 'doc', 'required', 'parent', kwargs)
        super(Spec, self).__init__()
        if name is not None:
            self['name'] = name
        if doc is not None:
            self['doc'] = doc
        if not required:
            self['required'] = required
        self._parent = parent

    @property
    def doc(self):
        ''' Documentation on what this Spec is specifying '''
        return self.get('doc', None)

    @property
    def name(self):
        ''' The name of the object being specified '''
        return self.get('name', None)

    @property
    def parent(self):
        ''' The parent specification of this specification '''
        return self._parent

    @parent.setter
    def parent(self, spec):
        ''' Set the parent of this specification '''
        if self._parent is not None:
            raise Exception('Cannot re-assign parent')
        self._parent = spec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(Spec, cls).build_const_args(spec_dict)
        if 'doc' not in ret:
            raise ValueError("'doc' missing")
        return ret

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

_attr_args = [
        {'name': 'name', 'type': str, 'doc': 'The name of this attribute'},
        {'name': 'dtype', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'shape', 'type': (list, tuple), 'doc': 'the shape of this dataset', 'default': None},
        {'name': 'dims', 'type': (list, tuple), 'doc': 'the dimensions of this dataset', 'default': None},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required. ignored when "value" is specified', 'default': True},
        {'name': 'parent', 'type': 'AttributeSpec', 'doc': 'the parent of this spec', 'default': None},
        {'name': 'value', 'type': None, 'doc': 'a constant value for this attribute', 'default': None}
]
class AttributeSpec(Spec):
    ''' Specification for attributes
    '''

    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, dims, shape, required, parent, value = getargs('name', 'dtype', 'doc', 'dims', 'shape', 'required', 'parent', 'value', kwargs)
        super().__init__(doc, name=name, required=required, parent=parent)
        if isinstance(dtype, type):
            self['dtype'] = dtype.__name__
        elif dtype is not None:
            self['dtype'] = dtype
        if value is not None:
            self.pop('required', None)
            self['value'] = value
        if dims is not None:
            self['dims'] = dims
            if 'shape' not in self:
                self['shape'] = tuple([None] * len(dims))
            else:
                if len(self['dims']) != len(self['shape']):
                    raise ValueError("'dims' and 'shape' must be the same length")

    @property
    def dtype(self):
        ''' The data type of the attribute '''
        return self.get('dtype', None)

    @property
    def value(self):
        ''' The constant value of the attribute. "None" if this attribute is not constant '''
        return self.get('value', None)

    @property
    def required(self):
        ''' True if this attribute is required, False otherwise. '''
        return self.get('required', None)

    @property
    def dims(self):
        ''' The dimensions of this attribute's value '''
        return self.get('dims', None)

    @property
    def shape(self):
        ''' The shape of this attribute's value '''
        return self.get('shape', None)

#    def verify(self, value):
#        '''Verify value (from an object) against this attribute specification '''
#        err = dict()
#        if any(t.__name__ == self['type'] for t in type(value).__mro__):
#            err['name'] = self['name']
#            err['type'] = 'attribute'
#            err['reason'] = 'incorrect type'
#        if err:
#            return [err]
#        else:
#            return list()
#
_attrbl_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace for data_type_inc and/or data_type_def of this specification', 'default': None},
]
class BaseStorageSpec(Spec):
    ''' A specification for any object that can hold attributes. '''

    __inc_key = 'data_type_inc'
    __def_key = 'data_type_def'
    __type_key = 'data_type'

    @docval(*deepcopy(_attrbl_args))
    def __init__(self, **kwargs):
        name, doc, parent, quantity, attributes, linkable, data_type_def, data_type_inc, namespace =\
             getargs('name', 'doc', 'parent', 'quantity', 'attributes', 'linkable', 'data_type_def', 'data_type_inc', 'namespace', kwargs)
        if name == NAME_WILDCARD and data_type_def is None and data_type_inc is None:
            raise ValueError("Cannot create Group or Dataset spec with wildcard name without specifying 'data_type_def' and/or 'data_type_inc'")
        super().__init__(doc, name=name, parent=parent)
        self.__attributes = dict()
        if quantity in (ONE_OR_MANY, ZERO_OR_MANY):
            if name != NAME_WILDCARD:
                raise ValueError(("Cannot give specific name to something that can ",
                                  "exist multiple times: name='%s', quantity='%s'" % (name, quantity)))
        if quantity != 1:
            self['quantity'] = quantity
        if not linkable:
            self['linkable'] = False
        if data_type_inc is not None:
            self[self.inc_key()] = data_type_inc
            if namespace is None:
                raise ValueError("'namespace' must be specified when specifying '%s', '%s'" % (self.inc_key(), data_type_inc))
            self['namespace'] = namespace
        if data_type_def is not None:
            self.pop('required', None)
            self[self.def_key()] = data_type_def
            if namespace is None:
                raise ValueError("'namespace' must be specified when specifying '%s', '%s'" % (self.def_key(), data_type_def))
            self['namespace'] = namespace

            self.set_attribute(self.get_data_type_spec(data_type_def))
            self.set_attribute(self.get_namespace_spec(namespace))

        for attribute in attributes:
            self.set_attribute(attribute)

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @classmethod
    def get_data_type_spec(cls, data_type_def):
        return AttributeSpec(cls.type_key(), 'text', 'the data type of this object', value=data_type_def)

    @classmethod
    def get_namespace_spec(cls, namespace):
        return AttributeSpec('namespace', 'text', 'the namespace for the data type of this object', value=namespace)

    @property
    def attributes(self):
        ''' The attributes for this specification '''
        return tuple(self.get('attributes', tuple()))

    @property
    def linkable(self):
        ''' True if object can be a link, False otherwise '''
        return self.get('linkable', None)

    @property
    def namespace(self):
        ''' The data type this specification defines '''
        return self.get('namespace', None)

    @property
    def data_type(self):
        return self.get(self.def_key(), self.get(self.inc_key(), None))

    @classmethod
    def type_key(cls):
        ''' Get the key used to store data type on an instance

        Override this method to use a different name for 'data_type'
        '''
        return cls.__type_key

    @classmethod
    def inc_key(cls):
        ''' Get the key used to define a data_type include.

        Override this method to use a different keyword for 'data_type_inc'
        '''
        return cls.__inc_key

    @classmethod
    def def_key(cls):
        ''' Get the key used to define a data_type definition.

        Override this method to use a different keyword for 'data_type_def'
        '''
        return cls.__def_key

    @property
    def data_type_inc(self):
        ''' The data type of this specification '''
        return self.get(self.inc_key(), self.data_type_def)

    @property
    def data_type_def(self):
        ''' The data type this specification defines '''
        return self.get(self.def_key(), None)

    @property
    def quantity(self):
        ''' The number of times the object being specified should be present '''
        return self.get('quantity', 1)

    @docval(*deepcopy(_attr_args))
    def add_attribute(self, **kwargs):
        ''' Add an attribute to this specification '''
        doc, name = kwargs.pop('doc', 'name')
        spec = AttributeSpec(doc, name, **kwargs)
        self.set_attribute(spec)
        return spec

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification for the attribute to add'})
    def set_attribute(self, **kwargs):
        ''' Set an attribute on this specification '''
        spec = kwargs.get('spec')
        #spec.set_parent(self)
        self.setdefault('attributes', list()).append(spec)
        self.__attributes[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def get_attribute(self, **kwargs):
        ''' Get an attribute on this specification '''
        name = getargs('name', kwargs)
        return self.__attributes.get(name)

#    def verify(self, builder):
#        ''' Verify that a builder meets this specification '''
#        errors = list()
#        if isinstance(dset_builder, LinkBuilder):
#            if not self['linkable']:
#                errors.append({'name': self['name'],
#                               'type': 'dataset',
#                               'reason': 'cannot be link'})
#        for attr_spec in self.attributes:
#            attr = builder.get(attr_spec['name'])
#            if attr:
#                for err in attr_spec.verify(attr):
#                    err['name'] = "%s.%s" % (self['name'], err['name'])
#                    errors.extend(err)
#            else:
#                errors.append({'name': "%s.%s" % (self['name'], attr_spec['name']),
#                               'type': 'attribute',
#                               'reason': 'missing'})
#        return errors
#
    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(BaseStorageSpec, cls).build_const_args(spec_dict)
        if 'attributes' in ret:
            ret['attributes'] = [AttributeSpec.build_spec(sub_spec) for sub_spec in ret['attributes']]
        return ret

_dataset_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'dtype', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'shape', 'type': (list, tuple), 'doc': 'the shape of this dataset', 'default': None},
        {'name': 'dims', 'type': (list, tuple), 'doc': 'the dimensions of this dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace for this specification', 'default': None},
]
class DatasetSpec(BaseStorageSpec):
    ''' Specification for datasets
    '''

    @docval(*deepcopy(_dataset_args))
    def __init__(self, **kwargs):
        doc, shape, dims, dtype = popargs('doc', 'shape', 'dims', 'dtype', kwargs)
        super(DatasetSpec, self).__init__(doc, **kwargs)
        if shape is not None:
            self['shape'] = shape
        if dims is not None:
            self['dims'] = dims
            if 'shape' not in self:
                self['shape'] = tuple([None] * len(dims))
            else:
                if len(self['dims']) != len(self['shape']):
                    raise ValueError("'dims' and 'shape' must be the same length")
        if dtype is not None:
            self['dtype'] = dtype

    @property
    def dims(self):
        ''' The dimensions of this Dataset '''
        return self.get('dims', None)

    @property
    def dtype(self):
        ''' The data type of the attribute '''
        return self.get('dtype', None)

    @property
    def shape(self):
        ''' The shape of the dataset '''
        return self.get('shape', None)

    @classmethod
    def __check_dim(cls, dim, data):
        return True

#    @docval({'name': 'dataset_builder', 'type': DatasetBuilder, 'doc': 'the builder object to verify'})
#    def verify(self, **kwargs):
#        ''' Verify that a DatasetBuilder meets this specification '''
#        # verify attributes
#        dataset_builder = kwargs['dataset_builder']
#        errors = super(DatasetSpec, self).verify(dataset_builder)
#        err = {'name': self['name'], 'type': 'dataset'}
#        if self.__check_dim(self['shape'], dataset_builder.data):
#            err['reason'] = 'incorrect shape'
#        if 'reason' in err:
#            errors.append(err)
#        return errors
#
_link_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this link represents'},
    {'name': 'target_type', 'type': str, 'doc': 'the target type GroupSpec or DatasetSpec'},
    {'name': 'name', 'type': str, 'doc': 'the name of this link', 'default': None}
]
class LinkSpec(Spec):

    @docval(*_link_args)
    def __init__(self, **kwargs):
        doc, target_type, name = popargs('doc', 'target_type', 'name', kwargs)
        super(LinkSpec, self).__init__(doc, name, **kwargs)
        self['target_type'] = target_type

    @property
    def data_type_inc(self):
        ''' The data type of target specification '''
        return self.get('target_type')

_group_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': None},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': str, 'doc': 'the NWB type this specification data_type_inc', 'default': None},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace for this specification', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    ''' Specification for groups
    '''

    @docval(*deepcopy(_group_args))
    def __init__(self, **kwargs):
        doc, groups, datasets, links = popargs('doc', 'groups', 'datasets', 'links', kwargs)
        super(GroupSpec, self).__init__(doc, **kwargs)
        self.__data_types = dict()
        self.__groups = dict()
        for group in groups:
            self.set_group(group)
        self.__datasets = dict()
        for dataset in datasets:
            self.set_dataset(dataset)
        self.__links = dict()
        for link in links:
            self.set_link(link)

    def __add_data_type_inc(self, spec):
        if spec.data_type_inc in self.__data_types:
            raise TypeError('Cannot have multipled data types of the same type without specifying name')
        self.__data_types[spec.data_type_inc] = spec

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data_type to retrieve'})
    def get_data_type(self, **kwargs):
        '''
        Get a specification by "data_type"
        '''
        ndt = getargs('data_type', kwargs)
        return self.__data_types.get(ndt, None)

    @property
    def groups(self):
        ''' The groups specificed in this GroupSpec '''
        return tuple(self.get('groups', tuple()))

    @property
    def datasets(self):
        ''' The datasets specificed in this GroupSpec '''
        return tuple(self.get('datasets', tuple()))

    @property
    def links(self):
        ''' The links specificed in this GroupSpec '''
        return tuple(self.get('links', tuple()))

    @docval(*deepcopy(_group_args))
    def add_group(self, **kwargs):
        ''' Add a new specification for a subgroup to this group specification '''
        doc = kwargs.pop('doc')
        spec = GroupSpec(doc, **kwargs)
        self.set_group(spec)
        return spec

    @docval({'name': 'spec', 'type': ('GroupSpec'), 'doc': 'the specification for the subgroup'})
    def set_group(self, **kwargs):
        ''' Add the given specification for a subgroup to this group specification '''
        spec = getargs('spec', kwargs)
        self.setdefault('groups', list()).append(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Group spec")
        else:
            self.__groups[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group to the Spec for'})
    def get_group(self, **kwargs):
        ''' Get a specification for a subgroup to this group specification '''
        name = getargs('name', kwargs)
        return self.__groups.get(name, self.__links.get(name))

    @docval(*deepcopy(_dataset_args))
    def add_dataset(self, **kwargs):
        ''' Add a new specification for a dataset to this group specification '''
        doc = kwargs.pop('doc')
        spec = DatasetSpec(doc, **kwargs)
        self.set_dataset(spec)
        return spec

    @docval({'name': 'spec', 'type': 'DatasetSpec', 'doc': 'the specification for the dataset'})
    def set_dataset(self, **kwargs):
        ''' Add the given specification for a dataset to this group specification '''
        spec = getargs('spec', kwargs)
        self.setdefault('datasets', list()).append(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            self.__datasets[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset to the Spec for'})
    def get_dataset(self, **kwargs):
        ''' Get a specification for a dataset to this group specification '''
        name = getargs('name', kwargs)
        return self.__datasets.get(name, self.__links.get(name))

    @docval(*_link_args)
    def add_link(self, **kwargs):
        ''' Add a new specification for a link to this group specification '''
        doc, target_type = popargs('doc', 'target_type', kwargs)
        spec = LinkSpec(doc, target_type, **kwargs)
        self.set_link(spec)
        return spec

    @docval({'name': 'spec', 'type': 'LinkSpec', 'doc': 'the specification for the object to link to'})
    def set_link(self, **kwargs):
        ''' Add a given specification for a link to this group specification '''
        spec = getargs('spec', kwargs)
        self.setdefault('links', list()).append(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            self.__links[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the link to the Spec for'})
    def get_dataset(self, **kwargs):
        ''' Get a specification for a dataset to this group specification '''
        name = getargs('name', kwargs)
        return self.__datasets.get(name, self.__links.get(name))

#    def verify(self, group_builder):
#        # verify attributes
#        errors = super(GroupSpec, self).verify(group_builder)
#        # verify datasets
#        for dset_spec in self['datasets']:
#            dset_builder = group_builder.get(dset_spec['name'])
#            if dset_builder:
#                for err in dset_spec.verify(dset_builder):
#                    err['name'] = "%s/%s" % (self['name'], err['name'])
#                    errors.append(error)
#            else:
#                errors.append({'name': "%s/%s" % (self['name'], dset_spec['name']),
#                               'type': 'dataset',
#                               'reason': 'missing'})
#        # verify groups
#        for group_spec in self['groups']:
#            subgroup_builder = group_builder.get(group_spec['name'])
#            if subgroup_builder:
#                for err in group_spec.verify(subgroup_builder):
#                    err['name'] = "%s/%s" % (self['name'], err['name'])
#                    errors.append(error)
#            else:
#                errors.append({'name': "%s/%s" % (self['name'], group_spec['name']),
#                               'type': 'group',
#                               'reason': 'missing'})
#        return errors
#
    @classmethod
    def dataset_spec_cls(cls):
        return DatasetSpec


    @classmethod
    def link_spec_cls(cls):
        return LinkSpec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        #ret = super(GroupSpec, cls).build_const_args(spec_dict)
        ret = super().build_const_args(spec_dict)
        if 'datasets' in ret:
            ret['datasets'] = list(map(cls.dataset_spec_cls().build_spec, ret['datasets']))
        if 'groups' in ret:
            ret['groups'] = list(map(cls.build_spec, ret['groups']))
        if 'links' in ret:
            ret['links'] = list(map(cls.link_spec_cls().build_spec, ret['links']))
        return ret

