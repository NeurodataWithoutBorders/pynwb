import abc
from itertools import chain
from pynwb.core import docval, getargs, popargs

import json
import copy
import sys

NAME_WILDCARD = None

class SpecCatalog(object):
    __specs = dict()

    @classmethod
    def register_spec(cls, obj_type, spec):
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        cls.__specs[type_name] = spec

    @classmethod
    def get_spec(cls, obj_type):
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        return cls.__specs.get(type_name, None)

    @classmethod
    def get_registered_types(cls):
        return tuple(cls.__specs.keys())

#
#{'groups': [
#    {'name': '/',
#     'attributes': [{'name': 'descriptions', ...} ... ]
#

#def get_path(spec):
#    if spec.parent = None:
#        return spec['name']
#    else:
#        if isinstance(spec, AttributeSpec):
#            sep = '.'
#        else:
#            sep = '/'
#        return "%s%s%s" % (get_spec(spec.parent), sep, spec['name']
#

class Spec(dict, metaclass=abc.ABCMeta):
    """ A base specification class
    """

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this attribute', 'default': None},
            {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': None},
            {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
            {'name': 'parent', 'type': 'AttributeSpec', 'doc': 'the parent of this spec', 'default': None})
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

    #def set_parent(self, spec):
    #    #self._parent = spec
    #    pass

_attr_args = [
        {'name': 'name', 'type': str, 'doc': 'The name of this attribute'},
        {'name': 'dtype', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': None},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
        {'name': 'parent', 'type': 'AttributeSpec', 'doc': 'the parent of this spec', 'default': None},
        {'name': 'value', 'type': None, 'doc': 'a constant value for this attribute', 'default': None}
]
class AttributeSpec(Spec):
    """ Specification for attributes
    """

    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, required, parent, required, value = getargs('name', 'dtype', 'doc', 'required', 'parent', 'required', 'value', kwargs)
        super().__init__(name=name, doc=doc, required=required, parent=parent)
        if isinstance(dtype, type):
            self['type'] = dtype.__name__
        else:
            self['type'] = dtype


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
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': None},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'extends', 'type': 'BaseStorageSpec', 'doc': 'the NWB type this specification extends', 'default': None},
]
class BaseStorageSpec(Spec):
    """ A specification for any object that can hold attributes.
    """
    @docval(*copy.deepcopy(_attrbl_args))
    def __init__(self, **kwargs):
        name, doc, parent, required, attributes, linkable, neurodata_type = getargs('name', 'doc', 'parent', 'required', 'attributes', 'linkable', 'neurodata_type', kwargs)
        if name == NAME_WILDCARD and neurodata_type is None:
            raise ValueError("Cannot create Group or Dataset spec with wildcard name without specifying 'neurodata_type'")
        super().__init__(name=name, doc=doc, required=required, parent=parent)
        self.__attributes = dict()
        for attribute in attributes:
            self.set_attribute(attribute)
        if not linkable:
            self['linkable'] = linkable
        if neurodata_type is not None:
            self['neurodata_type'] = neurodata_type
        extends = getargs('extends', kwargs)
        if extends is not None:
            self['extends'] = extends

    @property
    def attributes(self):
        return self['attributes']

    @property
    def linkable(self):
        return self['linkable']

    @property
    def neurodata_type(self):
        return self['neurodata_type']

    @docval(*copy.deepcopy(_attr_args))
    def add_attribute(self, **kwargs):
        """ Add an attribute to this object
        """
        name = kwargs.pop('name')
        if isinstance(name, AttributeSpec):
            spec = copy.deepcopy(name)
        else:
            spec = AttributeSpec(name, **kwargs)
        #attr.set_parent(self)
        self['attributes'].append(attr)
        return spec

    @docval({'name': 'spec', 'type': 'AttributeSpec', 'doc': 'the specification for the attribute to add'})
    def set_attribute(self, **kwargs):
        spec = kwargs.get('spec')
        #spec.set_parent(self)
        self.setdefault('attributes', list()).append(spec)
        self.__attributes[spec.name] = spec
        return spec

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

_dset_args = [
        {'name': 'dtype', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': None},
        {'name': 'dimensions', 'type': tuple, 'doc': 'the dimensions of this dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': None},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
]
class DatasetSpec(BaseStorageSpec):
    """ Specification for datasets
    """

    @docval(*copy.deepcopy(_dset_args))
    def __init__(self, **kwargs):
        super(DatasetSpec, self).__init__(**kwargs)
        dimensions, dtype = getargs('dimensions', 'dtype', kwargs)
        self['dimensions'] = dimensions
        self['type'] = dtype

    @property
    def dimensions(self):
        return self['dimensions']

    @classmethod
    def __check_dim(cls, dim, data):
        return True

    def verify(self, dataset_builder):
        # verify attributes
        errors = super(DatasetSpec, self).verify(dataset_builder)
        err = {'name': self['name'], 'type': 'dataset'}
        if self.__check_dim(self['dimensions'], dataset_builder.data):
            err['reason'] = 'incorrect dimensions'
        if 'reason' in err:
            errors.append(err)
        return errors

class LinkSpec(Spec):

    @docval({'name': 'target_spec', 'type': BaseStorageSpec, 'doc': 'the specification for the dataset'},
            {'name': 'name', 'type': str, 'doc': 'the name of this link', 'default': None})
    def __init__(self, **kwargs):
        spec, name = getargs('target_spec', 'name', kwargs)
        super(LinkSpec, self).__init__(name)
        self['target_spec'] = spec

    @property
    def neurodata_type(self):
        return self['target_spec'].get('neurodata_type', None)

_group_args = [
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': None},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': None},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'neurodata_type', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    """ Specification for groups
    """

    @docval(*copy.deepcopy(_group_args))
    def __init__(self, **kwargs):
        super(GroupSpec, self).__init__(**kwargs)
        groups, datasets, links, neurodata_type = getargs('groups', 'datasets', 'links', 'neurodata_type', kwargs)
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
        return self['groups']

    @property
    def datasets(self):
        return self['datasets']

    @property
    def links(self):
        return self['links']

    @docval(*copy.deepcopy(_group_args))
    def add_group(self, **kwargs):
        """ Add a group to this group spec
        """
        name = kwargs.pop('name')
        spec = GroupSpec(name, **kwargs)
        self.set_group(spec)
        return spec

    @docval({'name': 'spec', 'type': 'GroupSpec', 'doc': 'the specification for the subgroup'})
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

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group to the Spec for'})
    def get_group(self, **kwargs):
        name = getargs('name', kwargs)
        return self.__groups.get(name, self.__links.get(name))

    @docval(*copy.deepcopy(_dset_args))
    def add_dataset(self, **kwargs):
        """ Add a dataset to this group spec
        """
        name = kwargs.pop('name')
        spec = DatasetSpec(name, **kwargs)
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

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset to the Spec for'})
    def get_dataset(self, **kwargs):
        name = getargs('name', kwargs)
        return self.__datasets.get(name, self.__links.get(name))

    @docval({'name': 'target_spec', 'type': BaseStorageSpec, 'doc': 'the specification for the dataset'},
            {'name': 'name', 'type': str, 'doc': 'the name of this link', 'default': None})
    def add_link(self, **kwargs):
        target_spec = popargs('target_spec', kwargs)
        spec = LinkSpec(target_spec, **kwargs)
        self.set_link(spec)
        return spec

    @docval({'name': 'spec', 'type': LinkSpec, 'doc': 'the specification for the object to link to'})
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

    def template(self):
        builder = GroupBuilder()
        for group_spec in self['groups']:
            builder.add_group(group_spec['name'], builder=group_spec.template())
        return builder


