import abc
from itertools import chain
from pynwb.core import docval

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

    def __init__(self, name, doc=None, required=True, parent=None):
        self['name'] = name
        self['doc'] = doc
        self['required'] = required

    @abc.abstractmethod
    def verify(self):
        return True

    @property
    def name(self):
        return self['name']

    @property
    def parent(self):
        return self._parent

    def set_parent(self, spec):
        self._parent = spec

_attr_args = [
        {'name': 'name', 'type': str, 'doc': 'The name of this attribute'},
        {'name': 'dtype', 'type': str, 'doc': 'The data type of this attribute'},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
        {'name': 'parent', 'type': 'AttributeSpec', 'doc': 'the parent of this spec', 'default': None},
        {'name': 'value', 'type': None, 'doc': 'whether or not this attribute is a constant', 'default': None}
]
class AttributeSpec(Spec):
    """ Specification for attributes
    """
    
    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, required, parent, required, value = getargs('name', 'dtype', 'doc', 'required', 'parent', 'required', 'value', **kwargs)
        super().__init__(name, doc=doc, required=required, parent=parent)
        if isinstance(dtype, type):
            self['type'] = dtype.__name__
        

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
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': '*'},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'nwb_type', 'type': bool, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'extends', 'type': str, 'doc': 'the NWB type this specification extends', 'default': None},
]
class BaseStorageSpec(Spec):
    """ A specification for any object that can hold attributes.
    """
    @docval(*_attrbl_args)
    def __init__(self, **kwargs):
        name, doc, parent, required, attributes, linkable, nwb_type = getargs('name', 'doc', 'parent', 'required', 'attributes', 'linkable', 'nwb_type', **kwargs)
        super().__init__(name, doc=doc, required=required, parent=parent)
        self['attributes'] = attributes
        self['linkable'] = linkable
        if nwb_type:
            self['type'] = nwb_type
        extends = getargs('extends', **kwargs)
        if extends:
            self['extends'] = extends

    @property
    def attributes(self):
        return self['attributes']

    # TODO: figure this out 12/15/16
    @property
    def get_attribute(self, name):
        return self['attributes'].get(name, None)

    @property
    def linkable(self):
        return self['linkable']

    @docval(*_attr_args)
    def add_attribute(self, **kwargs):
        """ Add an attribute to this object
        """
        name = kwargs.pop('name')
        if isinstance(name, AttributeSpec):
            spec = copy.deepcopy(name)
        else:
            spec = AttributeSpec(name, **kwargs)
        attr.set_parent(self)
        self['attributes'].append(attr)
        return spec

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
        {'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset', 'default': '*'},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'nwb_type', 'type': bool, 'doc': 'the NWB type this specification represents', 'default': None},
]
class DatasetSpec(BaseStorageSpec):
    """ Specification for datasets
    """

    @docval(*_dset_args)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self['dimensions'] = dimensions

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

_group_args = [
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': '*'},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents', 'default': True},
        {'name': 'required', 'type': bool, 'doc': 'whether or not this group is required', 'default': True},
        {'name': 'nwb_type', 'type': bool, 'doc': 'the NWB type this specification represents', 'default': None},
]
class GroupSpec(BaseStorageSpec):
    """ Specification for groups
    """
    
    @docval(*_group_args)
    def __init__(self, **kwargs):
        super(GroupSpec, self).__init__(**kwargs)
        self['groups'] = getargs('groups', kwargs)
        self['datasets'] = getargs('datasets', kwargs)
        self['links'] = getargs('links', kwargs)
        self['nwb_type'] = getargs('nwb_type', kwargs)
    
    @property
    def groups(self):
        return self['groups']
    
    @property
    def datasets(self):
        return self['datasets']

    @property
    def links(self):
        return self['links']

    @docval(*_group_args)
    def add_group(self, **kwargs):
        """ Add a group to this group spec
        """
        name = kwargs.pop('name')
        if isinstance(name, GroupSpec):
            spec = copy.deepcopy(name)
        else:
            spec = GroupSpec(name, **kwargs)
        spec.set_parent(self)
        self['groups'].append(spec)
        return spec
    
    @docval(*_dset_args)
    def add_dataset(self, **kwargs):
        """ Add a dataset to this group spec
        """
        name = kwargs.pop('name')
        if isinstance(name, DatasetSpec):
            spec = copy.deepcopy(name)
        else:
            spec = DatasetSpec(name, **kwargs)
        spec.set_parent(self)
        self['datasets'].append(spec)
        return spec

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
