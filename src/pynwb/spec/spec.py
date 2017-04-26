import abc
from datetime import datetime
from copy import deepcopy
from pynwb.core import docval, getargs, popargs, get_docval

NAME_WILDCARD = None
ZERO_OR_ONE = '?'
ZERO_OR_MANY = '*'
ONE_OR_MANY = '+'
FLAGS = {
    'zero_or_one': ZERO_OR_ONE,
    'zero_or_many': ZERO_OR_MANY,
    'one_or_many': ONE_OR_MANY
}

class Spec(dict, metaclass=abc.ABCMeta):
    ''' A base specification class
    '''

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
            {'name': 'name', 'type': str, 'doc': 'The name of this attribute', 'default': None},
            {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
            {'name': 'parent', 'type': 'Spec', 'doc': 'the parent of this spec', 'default': None})
    def __init__(self, **kwargs):
        name, doc, required, parent = getargs('name', 'doc', 'required', 'parent', kwargs)
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

#    @abc.abstractmethod
#    def verify(self):
#        ''' A method to verify if a value meets this specification '''
#        return True
#
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
        ret = deepcopy(spec_dict)
        if 'doc' not in ret:
            identifer = None
            if 'name' in ret:
                identifier = "name '%s'" % ret['name']
            elif 'neurodata_type_def' in ret:
                identifier = "neurodata_type_def '%s'" % ret['neurodata_type_def']
            elif 'neurodata_type' in ret:
                identifier = "neurodata_type '%s'" % ret['neurodata_type']
            raise ValueError("doc missing in spec with %s" % identifier)
        return ret

    @classmethod
    def build_spec(cls, spec_dict):
        ''' Build a Spec object from the given Spec dict '''
        kwargs = cls.build_const_args(spec_dict)
        try:
            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)

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
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
]
class BaseStorageSpec(Spec):
    ''' A specification for any object that can hold attributes. '''

    @docval(*deepcopy(_attrbl_args))
    def __init__(self, **kwargs):
        name, doc, parent, quantity, attributes, linkable, neurodata_type_def, neurodata_type = getargs('name', 'doc', 'parent', 'quantity', 'attributes', 'linkable', 'neurodata_type_def', 'neurodata_type', kwargs)
        if name == NAME_WILDCARD and neurodata_type_def is None and neurodata_type is None:
            raise ValueError("Cannot create Group or Dataset spec with wildcard name without specifying 'neurodata_type_def' and/or 'neurodata_type'")
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
        if neurodata_type is not None:
            self['neurodata_type'] = neurodata_type
        if neurodata_type_def is not None:
            self.pop('required', None)
            self['neurodata_type_def'] = neurodata_type_def
        for attribute in attributes:
            self.set_attribute(attribute)

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @property
    def attributes(self):
        ''' The attributes for this specification '''
        return tuple(self.get('attributes', tuple()))

    @property
    def linkable(self):
        ''' True if object can be a link, False otherwise '''
        return self.get('linkable', None)

    @property
    def neurodata_type_def(self):
        ''' The neurodata type this specification defines '''
        return self.get('neurodata_type_def', None)

    @property
    def neurodata_type(self):
        ''' The neurodata type of this specification '''
        return self.get('neurodata_type', self.neurodata_type_def)

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
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
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
    def neurodata_type(self):
        ''' The neurodata type of target specification '''
        if isinstance(self['target_type'], dict):
            return self['target_type'].get('neurodata_type', None)
        elif isinstance(self['target_type'], str):
            return self['target_type']
        else:
            None

_group_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': None},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification neurodata_type', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    ''' Specification for groups
    '''

    @docval(*deepcopy(_group_args))
    def __init__(self, **kwargs):
        doc, groups, datasets, links = popargs('doc', 'groups', 'datasets', 'links', kwargs)
        super(GroupSpec, self).__init__(doc, **kwargs)
        self.__neurodata_types = dict()
        self.__groups = dict()
        for group in groups:
            self.set_group(group)
        self.__datasets = dict()
        for dataset in datasets:
            self.set_dataset(dataset)
        self.__links = dict()
        for link in links:
            self.set_link(link)

    def __add_neurodata_type(self, spec):
        if spec.neurodata_type in self.__neurodata_types:
            raise TypeError('Cannot have multipled neurodata types of the same type without specifying name')
        self.__neurodata_types[spec.neurodata_type] = spec

    @docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to retrieve'})
    def get_neurodata_type(self, **kwargs):
        '''
        Get a specification by "neurodata_type"
        '''
        ndt = getargs('neurodata_type', kwargs)
        return self.__neurodata_types.get(ndt, None)

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
            if spec.neurodata_type is not None:
                self.__add_neurodata_type(spec)
            else:
                raise TypeError("must specify 'name' or 'neurodata_type' in Group spec")
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
            if spec.neurodata_type is not None:
                self.__add_neurodata_type(spec)
            else:
                raise TypeError("must specify 'name' or 'neurodata_type' in Dataset spec")
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
            if spec.neurodata_type is not None:
                self.__add_neurodata_type(spec)
            else:
                raise TypeError("must specify 'name' or 'neurodata_type' in Dataset spec")
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
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(GroupSpec, cls).build_const_args(spec_dict)
        if 'datasets' in ret:
            ret['datasets'] = list(map(DatasetSpec.build_spec, ret['datasets']))
        if 'groups' in ret:
            ret['groups'] = list(map(GroupSpec.build_spec, ret['groups']))
        if 'links' in ret:
            ret['links'] = list(map(LinkSpec.build_spec, ret['links']))
        return ret


class SpecCatalog(object):

    def __init__(self):
        '''
        Create a new catalog for storing specifications

        ** Private Instance Variables **

        :ivar __specs: Dict with the specification of each registered type
        :ivar __parent_types: Dict with parent types for each registered type
        :ivar __spec_source_files: Dict with the path to the source files (if available) for each registered type
        :ivar __hierarchy: Dict describing the hierarchy for each registered type.
                    NOTE: Always use SpecCatalog.get_hierarchy(...) to retrieve the hierarchy
                    as this dictionary is used like a cache, i.e., to avoid repeated calcuation
                    of the hierarchy but the contents are computed on first request by SpecCatalog.get_hierarchy(...)

        '''
        self.__specs = dict()
        self.__parent_types = dict()
        self.__hierarchy = dict()
        self.__spec_source_files = dict()

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            {'name': 'spec', 'type': BaseStorageSpec, 'doc': 'a Spec object'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def register_spec(self, **kwargs):
        '''
        Associate a specified object type with an HDF5 specification
        '''
        obj_type, spec, source_file = getargs('obj_type', 'spec', 'source_file', kwargs)
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        if type_name in self.__specs:
            raise ValueError("'%s' - cannot overwrite existing specification" % type_name)
        self.__specs[type_name] = spec
        self.__spec_source_files[type_name] = source_file
        ndt = spec.neurodata_type
        ndt_def = spec.neurodata_type_def
        if ndt_def != ndt:
            self.__parent_types[ndt_def] = ndt

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            returns="the specification for writing the given object type to HDF5 ", rtype='Spec')
    def get_spec(self, **kwargs):
        '''
        Get the Spec object for the given type
        '''
        obj_type = getargs('obj_type', kwargs)
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        return self.__specs.get(type_name, None)

    def get_registered_types(self):
        '''
        Return all registered specifications
        '''
        return tuple(self.__specs.keys())

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            returns="the path to source specification file from which the spec was orignially loaded or None ",
            rtype='str')
    def get_spec_source_file(self, **kwargs):
        '''
        Return the path to the source file from which the spec for the given
        type was loaded from. None is returned if no file path is available
        for the spec. Note: The spec in the file may not be identical to the
        object in case teh spec is modified after load.
        '''
        obj_type = getargs('obj_type', kwargs)
        return self.__spec_source_files.get(obj_type, None)

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the Spec object to register'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def auto_register(self, **kwargs):
        '''
        Register this specification and all sub-specification using neurodata_type as object type name
        '''
        spec, source_file = getargs('spec', 'source_file', kwargs)
        ndt = spec.neurodata_type_def
        if ndt is not None:
            self.register_spec(ndt, spec, source_file)
        for dataset_spec in spec.datasets:
            dset_ndt = dataset_spec.neurodata_type_def
            if dset_ndt is not None:
                self.register_spec(dset_ndt, dataset_spec, source_file)
        for group_spec in spec.groups:
            self.auto_register(group_spec, source_file)

    @docval({'name': 'neurodata_type', 'type': (str, type), 'doc': 'the neurodata_type to get the hierarchy of'})
    def get_hierarchy(self, **kwargs):
        ''' Get the extension hierarchy for the given neurodata_type '''
        neurodata_type = getargs('neurodata_type', kwargs)
        if isinstance(neurodata_type, type):
            neurodata_type = neurodata_type.__name__
        ret = self.__hierarchy.get(neurodata_type)
        if ret is None:
            hierarchy = list()
            parent = neurodata_type
            while parent is not None:
                hierarchy.append(parent)
                parent = self.__parent_types.get(parent)
            # store computed hierarchy for later
            tmp_hier = tuple(hierarchy)
            ret = tmp_hier
            while len(tmp_hier) > 0:
                self.__hierarchy[tmp_hier[0]] = tmp_hier
                tmp_hier = tmp_hier[1:]
        return ret

    def __copy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.copy(spec)
        return ret

    def __deepcopy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.deepcopy(spec)
        return ret


_namespace_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this namespace represents'},
    {'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
    {'name': 'catalog', 'type': SpecCatalog, 'doc': 'Catalog with the specifications associated with this namespace'},
    {'name': 'full_name', 'type': str, 'doc': 'extended full name of this namespace', 'default': None},
    {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
    {'name': 'date', 'type': (datetime, str), 'doc': "Date last modified or released. Formatting is %Y-%m-%d %H:%M:%S, e.g, 2017-04-25 17:14:13",
     'default': None},
    {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
    {'name': 'contact', 'type': (str, list), 'doc': 'List of emails. Ordering should be the same as for author', 'default': None}
]
class NamespaceSpec(Spec):
    """
    Specification of a Namespace of type specifications
    """
    @docval(*deepcopy(_namespace_args))
    def __init__(self, **kwargs):
        doc, catalog, full_name, version, date, author, contact  = \
            popargs('doc', 'catalog', 'full_name', 'version', 'date', 'author', 'contact', kwargs)
        super(NamespaceSpec, self).__init__(doc, **kwargs)
        if catalog is not None:
            self['catalog'] = catalog
        if full_name is not None:
            self['full_name'] = full_name
        if version is not None:
            self['version'] = version
        if date is not None:
            self['date'] = date
        if author is not None:
            self['author'] = author
        if contact is not None:
            self['contact'] = contact

    @classmethod
    def build_const_args(cls, spec_dict, spec_path):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        import warnings
        from glob import iglob
        try:
            import ruamel.yaml as yaml
        except ImportError:
            import yaml
        from itertools import chain
        from os.path import join

        ret = super(NamespaceSpec, cls).build_const_args(spec_dict)
        if 'author' in ret:
            if isinstance(ret['author'], str):
                ret['author'] = [ret['author'],]
        if 'contact' in ret:
            if isinstance(ret['contact'], str):
                ret['contact'] = [ret['contact'],]
        if 'date' in ret:
            try:
                ret['date'] = datetime.strptime('2017-04-25 17:14:13', "%Y-%m-%d %H:%M:%S")
            except ValueError:
                warnings.warn('Date for NamespaceSpec could not be converted to datetime. Storing raw string instead')
        spec_catalog = SpecCatalog()
        if 'schema' in ret:
            for s in ret['schema']:
                source_file = s.get('source', None)
                ntypes = s.get('neurodata_types', None)
                with open(source_file, 'r') as stream:
                    for obj in yaml.safe_load(stream):
                        spec_obj = GroupSpec.build_spec(obj)
                        if ntypes is None or spec_obj.neurodata_type_def in ntypes:
                            spec_catalog.auto_register(spec_obj,
                                                       source_file=source_file)
            ret.pop('schema')
        else:
            exts = ['yaml', 'json']
            glob_str = join(spec_path, "*.%s")
            for path in chain(*[iglob(glob_str % ext) for ext in exts]):
                with open(path, 'r') as stream:
                    for obj in yaml.safe_load(stream):
                        if obj != 'namespaces':
                            spec_obj = GroupSpec.build_spec(obj)
                            spec_catalog.auto_register(spec_obj,
                                                       source_file=path)
        ret['catalog'] = spec_catalog
        return ret

    @classmethod
    def from_file(cls, spec_file):
        """Build a Namespace spec from the given YAML file with the namespace definition"""
        try:
            import ruamel.yaml as yaml
        except ImportError:
            import yaml
        from os.path import dirname
        namespaces = []
        with open(spec_file, 'r') as stream:
            obj = yaml.load(stream, yaml.RoundTripLoader)
            if 'namespaces' in obj:
                for ns in obj['namespaces']:
                    namespaces.append(NamespaceSpec.build_spec(ns, dirname(spec_file)))
        if len(namespaces) == 1:
            return namespaces[0]
        else:
            return namespaces

    @classmethod
    def build_spec(cls, spec_dict, spec_path):
        """ Build a Spec object from the given Spec dict """
        kwargs = cls.build_const_args(spec_dict, spec_path)
        try:
            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)

    @property
    def full_name(self):
        """String with full name or None"""
        return self.get('full_name', None)

    @property
    def contact(self):
        """String or list of strings with the contacts or None"""
        return self.get('contact', None)

    @property
    def author(self):
        """String or list of strings with the authors or  None"""
        return self.get('author', None)

    @property
    def version(self):
        """String, list, or tuple with the version or None """
        return self.get('author', None)

    @property
    def date(self):
        """Date last modified or released.

        :return: datetime object, string, or None"""
        return self.get('full_name', None)

