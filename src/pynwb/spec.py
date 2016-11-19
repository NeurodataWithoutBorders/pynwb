#
#{'groups': [
#    {'name': '/',
#     'attributes': [{'name': 'descriptions', ...} ... ]
#

class BaseSpec(dict, metaclass=abc.ABCMeta):
    """ A base specification class
    """

    def __init__(self, name, doc=None, required=True):
        self['name'] = name
        self['doc'] = doc
        self['required'] = required

    @abc.abstractmethod
    def verify(self):
        return True

class AttributeSpec(BaseSpec):
    """ Specification for attributes
    """
    
    def __init__(self, name, dtype, doc=None, required=True):
        super().__init__(name, doc, required)
        if isinstance(dtype, type):
            self['type'] = dtype.__name__

    def verify(self, value):
        """Verify this attribute
        """
        err = dict()
        if any(t.__name__ == self['type'] for t in type(value).__mro__)
            err['name'] = self['name']
            err['type'] = 'attribute'
            err['reason'] = 'incorrect type' 
        if err:
            return [err]
        else:
            return list()

class AttributableSpec(BaseSpec):
    """ A specification for any object that can hold attributes.
    """
    def __init__(self, name, attributes=list(), doc=None, required=True, linkable=True):
        super().__init__(name, doc, required)
        self['attributes'] = attributes
        self['linkable'] = linktable

    def add_attribute(self, name, dtype, doc=None, required=True):
        """ Add an attribute to this object
        """
        spec = AttributeSpec(name, dtype, doc, required)
        spec['attributes'] = spec
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

class GroupSpec(AttributableSpec):
    """ Specification for groups
    """
    
    def __init__(self, name, groups=list(), datasets=list(), attributes=list(), linkable=True, doc=None, required=True):
        super().__init__(name, attributes, doc, required)
        self['linkable'] = linkable
        self['groups'] = groups
        self['datasets'] = datasets

    def add_group(self, name, groups=list(), datasets=list(), attributes=list(), linkable=True, doc=None, required=True):
        """ Add a group to this group spec
        """
        if isinstance(name, GroupSpec):
            spec = name
        else:
            spec = GroupSpec(name, groups, datasets, attributes, linkable, doc, required)
        self['groups'].append(spec)
        return spec
    
    def add_dataset(self, name, attributes=list(), dimensions=None, linkable=True, doc=None, required=True):
        """ Add a dataset to this group spec
        """
        if isinstance(name, DatasetSpec):
            spec = name
        else:
            spec = DatasetSpec(name, attributes, dimensions, linkable, doc, required)
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
                errors.append({'name': "%s/%s" % (self['name'] dset_spec['name']), 
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
                errors.append({'name': "%s/%s" % (self['name'] group_spec['name']), 
                               'type': 'group',
                               'reason': 'missing'})
        return errors

class DatasetSpec(AttributableSpec):
    """ Specification for datasets
    """

    def __init__(self, name, attributes=list(), dimensions=None, linkable=True, doc=None, required=True):
        super().__init__(name, attributes, doc, required)
        self['linkable'] = linkable
        self['dimensions'] = dimensions

    @classmethod
    def __check_dim(cls, dim, data):
        return True
    
    def verify(self, dataset_builder):
        # verify attributes
        errors = super(DatasetSpec, self).verify(dataset_builder)
        if self['dimensions']:
            err = {'name': self['name'], 'type': 'dataset'}
            if self.__check_dim(self['dimensions'], dataset_builder.data)
                err['reason'] = 'incorrect dimensions'
            if 'reason' in err:
                errors.append(err)
        return errors
