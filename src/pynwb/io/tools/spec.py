import abc
from copy import deepcopy

from pynwb.core import docval, getargs, popargs, get_docval

NAME_WILDCARD = None

class SpecCatalog(object):

    def __init__(self):
        self.__specs = dict()

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            {'name': 'spec', 'type': 'Spec', 'doc': 'a Spec object'})
    def register_spec(self, **kwargs):
        '''
        Associate a specified object type with an HDF5 specification
        '''
        obj_type, spec, register_map = getargs('obj_type', 'spec', 'register_map', kwargs)
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        if type_name in self.__specs:
            raise ValueError("'%s' - cannot overwrite existing specification" % type_name)
        self.__specs[type_name] = spec

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


class Spec(dict, metaclass=abc.ABCMeta):
    """ A base specification class
    """

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

    @abc.abstractmethod
    def verify(self):
        return True

    @property
    def name(self):
        return self.get('name', None)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, spec):
        self._parent = spec

    @classmethod
    def build_const_args(cls, spec_dict):
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
        {'name': 'type', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required. ignored when "value" is specified', 'default': True},
        {'name': 'parent', 'type': 'AttributeSpec', 'doc': 'the parent of this spec', 'default': None},
        {'name': 'value', 'type': None, 'doc': 'a constant value for this attribute', 'default': None}
]
class AttributeSpec(Spec):
    """ Specification for attributes
    """

    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, required, parent, value = getargs('name', 'type', 'doc', 'required', 'parent', 'value', kwargs)
        super().__init__(doc, name=name, required=required, parent=parent)
        if isinstance(dtype, type):
            self['type'] = dtype.__name__
        else:
            self['type'] = dtype
        if value is not None:
            self.pop('required', None)
            self['value'] = value

    @property
    def name(self):
        return self.get('name', None)

    @property
    def dtype(self):
        return self.get('type', None)

    @property
    def value(self):
        return self.get('value', None)

    @property
    def doc(self):
        return self.get('doc', None)

    @property
    def required(self):
        return self.get('required', None)

    def verify(self, value):
        """Verify value (from an object) against this attribute specification
        """
        err = dict()
        if any(t.__name__ == self['type'] for t in type(value).__mro__):
            err['name'] = self['name']
            err['type'] = 'attribute'
            err['reason'] = 'incorrect type'
        if err:
            return [err]
        else:
            return list()

_attrbl_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
]
class BaseStorageSpec(Spec):
    """ A specification for any object that can hold attributes.
    """

    @docval(*deepcopy(_attrbl_args))
    def __init__(self, **kwargs):
        name, doc, parent, required, attributes, linkable, neurodata_type_def, neurodata_type = getargs('name', 'doc', 'parent', 'required', 'attributes', 'linkable', 'neurodata_type_def', 'neurodata_type', kwargs)
        if name == NAME_WILDCARD and neurodata_type_def is None and neurodata_type is None:
            raise ValueError("Cannot create Group or Dataset spec with wildcard name without specifying 'neurodata_type_def' and/or 'neurodata_type'")
        super().__init__(doc, name=name, required=required, parent=parent)
        self.__attributes = dict()
        if not linkable:
            self['linkable'] = False
        if neurodata_type is not None:
            self['neurodata_type'] = neurodata_type
        if neurodata_type_def is not None:
            self.pop('required', None)
            self['neurodata_type_def'] = neurodata_type_def
        for attribute in attributes:
            self.set_attribute(attribute)

    @property
    def attributes(self):
        return tuple(self.get('attributes', tuple()))

    @property
    def linkable(self):
        return self.get('linkable', None)

    @property
    def neurodata_type_def(self):
        return self.get('neurodata_type_def', None)

    @property
    def neurodata_type(self):
        return self.get('neurodata_type', self.neurodata_type_def)

    @docval(*deepcopy(_attr_args))
    def add_attribute(self, **kwargs):
        """
        Add an attribute to this object
        """
        doc, name = kwargs.pop('doc', 'name')
        spec = AttributeSpec(doc, name, **kwargs)
        self.set_attribute(spec)
        return spec

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification for the attribute to add'})
    def set_attribute(self, **kwargs):
        spec = kwargs.get('spec')
        #spec.set_parent(self)
        self.setdefault('attributes', list()).append(spec)
        self.__attributes[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def get_attribute(self, **kwargs):
        name = getargs('name', kwargs)
        return self.__attributes.get(name)

    def verify(self, builder):
        errors = list()
        if isinstance(dset_builder, LinkBuilder):
            if not self['linkable']:
                errors.append({'name': self['name'],
                               'type': 'dataset',
                               'reason': 'cannot be link'})
        for attr_spec in self['attributes']:
            attr = builder.get(attr_spec['name'])
            if attr:
                for err in attr_spec.verify(attr):
                    err['name'] = "%s.%s" % (self['name'], err['name'])
                    errors.extend(err)
            else:
                errors.append({'name': "%s.%s" % (self['name'], attr_spec['name']),
                               'type': 'attribute',
                               'reason': 'missing'})
        return errors

    @classmethod
    def build_const_args(cls, spec_dict):
        ret = super(BaseStorageSpec, cls).build_const_args(spec_dict)
        if 'attributes' in ret:
            ret['attributes'] = [AttributeSpec.build_spec(sub_spec) for sub_spec in ret['attributes']]
        return ret

_dataset_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'type', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'shape', 'type': tuple, 'doc': 'the shape of this dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
]
class DatasetSpec(BaseStorageSpec):
    """ Specification for datasets
    """

    @docval(*deepcopy(_dataset_args))
    def __init__(self, **kwargs):
        doc, shape, dtype = popargs('doc', 'shape', 'type', kwargs)
        super(DatasetSpec, self).__init__(doc, **kwargs)
        if shape is not None:
            self['shape'] = shape
        if dtype is not None:
            self['type'] = dtype

    @property
    def shape(self):
        return self['shape']

    @classmethod
    def __check_dim(cls, dim, data):
        return True

    def verify(self, dataset_builder):
        # verify attributes
        errors = super(DatasetSpec, self).verify(dataset_builder)
        err = {'name': self['name'], 'type': 'dataset'}
        if self.__check_dim(self['shape'], dataset_builder.data):
            err['reason'] = 'incorrect shape'
        if 'reason' in err:
            errors.append(err)
        return errors

_link_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this link represents'},
    {'name': 'target_type', 'type': str, 'doc': 'the specification for the dataset'},
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
        return self['target_type'].get('neurodata_type', None)

_group_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': None},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification neurodata_type', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    """ Specification for groups
    """

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

    @property
    def groups(self):
        return tuple(self.get('groups', tuple()))

    @property
    def datasets(self):
        return tuple(self.get('datasets', tuple()))

    @property
    def links(self):
        return tuple(self.get('links', tuple()))

    @docval(*deepcopy(_group_args))
    def add_group(self, **kwargs):
        """ Add a group to this group spec
        """
        doc = kwargs.pop('doc')
        spec = GroupSpec(doc, **kwargs)
        self.set_group(spec)
        return spec

    @docval({'name': 'spec', 'type': ('GroupSpec', 'NeurodataTypeSpec'), 'doc': 'the specification for the subgroup'})
    def set_group(self, **kwargs):
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
        name = getargs('name', kwargs)
        return self.__groups.get(name, self.__links.get(name))

    @docval(*deepcopy(_dataset_args))
    def add_dataset(self, **kwargs):
        """ Add a dataset to this group spec
        """
        doc = kwargs.pop('doc')
        spec = DatasetSpec(doc, **kwargs)
        self.set_dataset(spec)
        return spec

    @docval({'name': 'spec', 'type': 'DatasetSpec', 'doc': 'the specification for the dataset'})
    def set_dataset(self, **kwargs):
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
        name = getargs('name', kwargs)
        return self.__datasets.get(name, self.__links.get(name))

    @docval(*_link_args)
    def add_link(self, **kwargs):
        doc, target_type = popargs('doc', 'target_type', kwargs)
        spec = LinkSpec(doc, target_type, **kwargs)
        self.set_link(spec)
        return spec

    @docval({'name': 'spec', 'type': 'LinkSpec', 'doc': 'the specification for the object to link to'})
    def set_link(self, **kwargs):
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

    def verify(self, group_builder):
        # verify attributes
        errors = super(GroupSpec, self).verify(group_builder)
        # verify datasets
        for dset_spec in self['datasets']:
            dset_builder = group_builder.get(dset_spec['name'])
            if dset_builder:
                for err in dset_spec.verify(dset_builder):
                    err['name'] = "%s/%s" % (self['name'], err['name'])
                    errors.append(error)
            else:
                errors.append({'name': "%s/%s" % (self['name'], dset_spec['name']),
                               'type': 'dataset',
                               'reason': 'missing'})
        # verify groups
        for group_spec in self['groups']:
            subgroup_builder = group_builder.get(group_spec['name'])
            if subgroup_builder:
                for err in group_spec.verify(subgroup_builder):
                    err['name'] = "%s/%s" % (self['name'], err['name'])
                    errors.append(error)
            else:
                errors.append({'name': "%s/%s" % (self['name'], group_spec['name']),
                               'type': 'group',
                               'reason': 'missing'})
        return errors

    @classmethod
    def build_const_args(cls, spec_dict):
        ret = super(GroupSpec, cls).build_const_args(spec_dict)
        if 'datasets' in ret:
            ret['datasets'] = list(map(DatasetSpec.build_spec, ret['datasets']))
        if 'groups' in ret:
            ret['groups'] = list(map(GroupSpec.build_spec, ret['groups']))
        if 'links' in ret:
            ret['links'] = list(map(LinkSpec.build_spec, ret['links']))
        return ret
