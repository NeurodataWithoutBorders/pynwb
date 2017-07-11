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
        {'name': 'value', 'type': None, 'doc': 'a constant value for this attribute', 'default': None},
        {'name': 'default_value', 'type': None, 'doc': 'a default value for this attribute', 'default': None}
]
class AttributeSpec(Spec):
    ''' Specification for attributes
    '''

    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, dims, shape, required, parent, value, default_value = getargs('name', 'dtype', 'doc', 'dims', 'shape', 'required', 'parent', 'value', 'default_value', kwargs)
        super().__init__(doc, name=name, required=required, parent=parent)
        if isinstance(dtype, type):
            self['dtype'] = dtype.__name__
        elif dtype is not None:
            self['dtype'] = dtype
        if value is not None:
            self.pop('required', None)
            self['value'] = value
        if default_value is not None:
            if value is not None:
                raise ValueError("cannot specify 'value' and 'default_value'")
            self['default_value'] = default_value
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
    def default_value(self):
        ''' The default value of the attribute. "None" if this attribute has no default value '''
        return self.get('default_value', None)

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
        {'name': 'data_type_inc', 'type': (str, 'BaseStorageSpec'), 'doc': 'the NWB type this specification extends', 'default': None},
]
class BaseStorageSpec(Spec):
    ''' A specification for any object that can hold attributes. '''

    __inc_key = 'data_type_inc'
    __def_key = 'data_type_def'
    __type_key = 'data_type'

    @docval(*deepcopy(_attrbl_args))
    def __init__(self, **kwargs):
        name, doc, parent, quantity, attributes, linkable, data_type_def, data_type_inc =\
             getargs('name', 'doc', 'parent', 'quantity', 'attributes', 'linkable', 'data_type_def', 'data_type_inc', kwargs)
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
        resolve = False
        if data_type_inc is not None:
            if isinstance(data_type_inc, BaseStorageSpec):
                self[self.inc_key()] = data_type_inc.data_type_def
            else:
                self[self.inc_key()] = data_type_inc
        if data_type_def is not None:
            self.pop('required', None)
            self[self.def_key()] = data_type_def
            if data_type_inc is not None and isinstance(data_type_inc, BaseStorageSpec):
                resolve = True
        for attribute in attributes:
            self.set_attribute(attribute)
        if resolve:
            self.resolve_spec(data_type_inc)

    @property
    def required(self):
        ''' Whether or not the this spec represents a required field '''
        return self.quantity not in (ZERO_OR_ONE, ZERO_OR_MANY)

    @docval({'name': 'inc_spec', 'type': 'BaseStorageSpec', 'doc': 'the data type this specification represents'})
    def resolve_spec(self, **kwargs):
        self.__new_attributes = set(self.__attributes.keys())
        inc_spec = getargs('inc_spec', kwargs)
        for attribute in inc_spec.attributes:
            self.__new_attributes.discard(attribute)
            if attribute.name in self.__attributes:
                continue
            self.set_attribute(attribute)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def is_inherited_attribute(self, **kwargs):
        name = getargs('name', kwargs)
        return name not in self.__new_attributes

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @classmethod
    def get_data_type_spec(cls, data_type_def):
        return AttributeSpec(cls.type_key(), 'text', 'the data type of this object', value=data_type_def)

    @classmethod
    def get_namespace_spec(cls):
        return AttributeSpec('namespace', 'text', 'the namespace for the data type of this object', required=False)

    @property
    def attributes(self):
        ''' The attributes for this specification '''
        return tuple(self.get('attributes', tuple()))

    @property
    def linkable(self):
        ''' True if object can be a link, False otherwise '''
        return self.get('linkable', None)

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
        return self.get(self.inc_key())

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
        attributes = self.setdefault('attributes', list())
        if spec.parent is not None:
            spec = AttributeSpec.build_spec(spec)
        if spec.name in self.__attributes:
            idx = -1
            for i, attribute in enumerate(attributes):
                if attribute.name == spec.name:
                    idx = i
                    break
            if idx >= 0:
                attributes[idx] = spec
            else:
                raise ValueError('%s in __attributes but not in spec record' % spec.name)
        else:
            attributes.append(spec)
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
        {'name': 'data_type_inc', 'type': (str, 'DatasetSpec'), 'doc': 'the NWB type this specification extends', 'default': None},
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
    {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
    {'name': 'name', 'type': str, 'doc': 'the name of this link', 'default': None}
]
class LinkSpec(Spec):

    @docval(*_link_args)
    def __init__(self, **kwargs):
        doc, target_type, name, quantity = popargs('doc', 'target_type', 'name', 'quantity', kwargs)
        super(LinkSpec, self).__init__(doc, name, **kwargs)
        self['target_type'] = target_type
        if quantity != 1:
            self['quantity'] = quantity

    @property
    def target_type(self):
        ''' The data type of target specification '''
        return self.get('target_type')

    @property
    def data_type_inc(self):
        ''' The data type of target specification '''
        return self.get('target_type')

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @property
    def quantity(self):
        ''' The number of times the object being specified should be present '''
        return self.get('quantity', 1)

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
        {'name': 'data_type_inc', 'type': (str, 'GroupSpec'), 'doc': 'the NWB type this specification data_type_inc', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    ''' Specification for groups
    '''

    @docval(*deepcopy(_group_args))
    def __init__(self, **kwargs):
        doc, groups, datasets, links = popargs('doc', 'groups', 'datasets', 'links', kwargs)
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
        self.__inherited_data_type_defs = set()
        super(GroupSpec, self).__init__(doc, **kwargs)

    @docval({'name': 'inc_spec', 'type': 'GroupSpec', 'doc': 'the data type this specification represents'})
    def resolve_spec(self, **kwargs):
        inc_spec = getargs('inc_spec', kwargs)
        self.__new_datasets = set(self.__datasets.keys())
        for dataset in inc_spec.datasets:
            self.__new_datasets.discard(dataset.name)
            if dataset.name in self.__datasets:
                self.__datasets[dataset.name].resolve_spec(dataset)
            else:
                self.set_dataset(dataset)
            if dataset.data_type_def is not None:
                self.__inherited_data_type_defs.add(dataset.data_type_def)
        self.__new_groups = set(self.__groups.keys())
        for group in inc_spec.groups:
            self.__new_groups.discard(group.name)
            if group.name in self.__groups:
                self.__groups[group.name].resolve_spec(group)
            else:
                self.set_group(group)
            if group.data_type_def is not None:
                self.__inherited_data_type_defs.add(group.data_type_def)
        self.__new_links = set(self.__links.keys())
        for link in inc_spec.links:
            self.__new_links.discard(link.name)
            if link.name in self.__links:
                continue
            self.set_link(link)
        super(GroupSpec, self).resolve_spec(inc_spec)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset'})
    def is_inherited_dataset(self, **kwargs):
        '''Return true of a dataset with the given name was inherited'''
        name = getargs('name', kwargs)
        return name not in self.__new_dataset

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group'})
    def is_inherited_group(self, **kwargs):
        '''Return true of a group with the given name was inherited'''
        name = getargs('name', kwargs)
        return name not in self.__new_group

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the link'})
    def is_inherited_link(self, **kwargs):
        '''Return true of a link with the given name was inherited'''
        name = getargs('name', kwargs)
        return name not in self.__new_link

    @docval({'name': 'spec', 'type': 'BaseStorageSpec', 'doc': 'the specification to check'})
    def is_inherited(self, **kwargs):
        ''' Returns True if `spec` represents a spec that was inherited from an included data_type '''
        spec = getargs('spec', kwargs)
        if spec.data_type_def is None:
            raise ValueError('cannot check if something was inherited if it does not have a %s' % self.def_key())
        return spec.data_type_def in self.__inherited_data_type_defs

    def __add_data_type_inc(self, spec):
        dt = None
        if hasattr(spec, 'data_type_def') and spec.data_type_def is not None:
            dt = spec.data_type_def
        elif hasattr(spec, 'data_type_inc') and spec.data_type_inc is not None:
            dt = spec.data_type_inc
        if not dt:
            raise TypeError("spec does not have '%s' or '%s' defined" % (self.def_key(), self.inc_key()))
        if dt in self.__data_types:
            raise TypeError('Cannot have multipled data types of the same type without specifying name')
        self.__data_types[dt] = spec

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
        if spec.parent is not None:
            spec = GroupSpec.build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Group spec")
        else:
            self.__groups[spec.name] = spec
        self.setdefault('groups', list()).append(spec)
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
        if spec.parent is not None:
            spec = DatasetSpec.build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            self.__datasets[spec.name] = spec
        self.setdefault('datasets', list()).append(spec)
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
        if spec.parent is not None:
            spec = LinkSpec.build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            self.__links[spec.name] = spec
        self.setdefault('links', list()).append(spec)
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
        ''' The class to use when constructing DatasetSpec objects

            Override this if extending to use a class other than DatasetSpec to build
            dataset specifications
        '''
        return DatasetSpec


    @classmethod
    def link_spec_cls(cls):
        ''' The class to use when constructing LinkSpec objects

            Override this if extending to use a class other than LinkSpec to build
            link specifications
        '''
        return LinkSpec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super().build_const_args(spec_dict)
        if 'datasets' in ret:
            ret['datasets'] = list(map(cls.dataset_spec_cls().build_spec, ret['datasets']))
        if 'groups' in ret:
            ret['groups'] = list(map(cls.build_spec, ret['groups']))
        if 'links' in ret:
            ret['links'] = list(map(cls.link_spec_cls().build_spec, ret['links']))
        return ret

