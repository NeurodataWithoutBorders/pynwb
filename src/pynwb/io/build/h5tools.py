class GroupBuilder(dict):
    __link = 'links'
    __group = 'groups'
    __dataset = 'datasets'
    __attribute = 'attributes'

    @docval({'name':'groups', 'type': dict, 'doc': 'a dictionary of subgroups to create in this group', 'default': dict()},
            {'name':'datasets', 'type': dict, 'doc': 'a dictionary of datasets to create in this group', 'default': dict()},
            {'name':'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this group', 'default': dict()},
            {'name':'links', 'type': dict, 'doc': 'a dictionary of links to create in this group', 'default': dict()})
    def __init__(self, groups=dict(), datasets=dict(), attributes=dict(), links=dict()):
        """
        Create a GroupBuilder object
        """
        super().__init__()
        super().__setitem__(GroupBuilder.__group, dict())
        super().__setitem__(GroupBuilder.__dataset, dict())
        super().__setitem__(GroupBuilder.__attribute, dict())
        super().__setitem__(GroupBuilder.__link, dict())
        self.obj_type = dict()
        for name, group in groups.items():
            self.set_group(name, group)
        for name, dataset in datasets.items():
            self.set_dataset(name, dataset)
        for name, link in links.items():
            self.set_link(name, link)
        for name, val in attributes.items():
            self.set_attribute(name, val)

    @property
    def groups(self):
        return super().__getitem__(GroupBuilder.__group)

    @property
    def datasets(self):
        return super().__getitem__(GroupBuilder.__dataset)

    @property
    def attributes(self):
        return super().__getitem__(GroupBuilder.__attribute)

    @property
    def links(self):
        return super().__getitem__(GroupBuilder.__link)

    def __set_builder(self, name, builder, obj_type):
        if name in self.obj_type:
            if self.obj_type[name] != obj_type:
                raise KeyError("'%s' already exists as %s" % (name, self.obj_type[name]))
        super().__getitem__(obj_type)[name] = builder
        self.obj_type[name] = obj_type

    @docval({'name':'name', 'type': str, 'doc': 'the name of this dataset'},
            {'name':'data', 'type': None, 'doc': 'a dictionary of datasets to create in this dataset', 'default': None},
            {'name':'dtype', 'type': type, 'doc': 'the datatype of this dataset', 'default': None},
            {'name':'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this dataset', 'default': dict()},
            {'name':'maxshape', 'type': (int, tuple), 'doc': 'the shape of this dataset. Use None for scalars', 'default': None},
            {'name':'chunks', 'type': bool, 'doc': 'whether or not to chunk this dataset', 'default': False},
            returns='the DatasetBuilder object for the dataset', rtype='DatasetBuilder')
    def add_dataset(self, **kwargs):
        """
        Create a dataset and add it to this group
        """
        name = kwargs.pop('name')
        builder = DatasetBuilder(**kwargs)
        self.set_dataset(name, builder)
        return builder

    @docval({'name':'name', 'type': str, 'doc': 'the name of this dataset'},
            {'name':'builder', 'type': 'DatasetBuilder', 'doc': 'the GroupBuilder that represents this dataset'})
    def set_dataset(self, **kwargs):
        """
        Add a dataset to this group
        """
        name, builder, = getargs('name', 'builder', kwargs)
        self.__set_builder(name, builder, GroupBuilder.__dataset)

    @docval({'name':'name', 'type': str, 'doc': 'the name of this subgroup'},
            {'name':'groups', 'type': dict, 'doc': 'a dictionary of subgroups to create in this subgroup', 'default': dict()},
            {'name':'datasets', 'type': dict, 'doc': 'a dictionary of datasets to create in this subgroup', 'default': dict()},
            {'name':'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this subgroup', 'default': dict()},
            {'name':'links', 'type': dict, 'doc': 'a dictionary of links to create in this subgroup', 'default': dict()},
            returns='the GroupBuilder object for the subgroup', rtype='GroupBuilder')
    def add_group(self, **kwargs):
        """
        Add a subgroup with the given data to this group
        """
        name = kwargs.pop('name')
        builder = GroupBuilder(**kwargs)
        self.set_group(name, builder)
        return builder

    @docval({'name':'name', 'type': str, 'doc': 'the name of this subgroup'},
            {'name':'builder', 'type': 'GroupBuilder', 'doc': 'the GroupBuilder that represents this subgroup'})
    def set_group(self, **kwargs):
        """
        Add a subgroup to this group
        """
        name, builder, = getargs('name', 'builder', kwargs)
        self.__set_builder(name, builder, GroupBuilder.__group)

    @docval({'name':'name', 'type': str, 'doc': 'the name of this link'},
            {'name':'path', 'type': str, 'doc': 'the path within this HDF5 file'},
            returns='the builder object for the soft link', rtype='LinkBuilder')
    def add_link(self, **kwargs):
        """
        Create a soft link and add it to this group.
        """
        name, path = getargs('name', 'path', kwargs)
        builder = LinkBuilder(path)
        self.set_link(name, builder)
        return builder

    @docval({'name':'name', 'type': str, 'doc': 'the name of this link'},
            {'name':'file_path', 'type': str, 'doc': 'the file path of this external link'},
            {'name':'path', 'type': str, 'doc': 'the absolute path within the external HDF5 file'},
            returns='the builder object for the external link', rtype='ExternalLinkBuilder')
    def add_external_link(self, **kwargs):
        """
        Create an external link and add it to this group.
        """
        name, file_path, path = getargs('name', 'file_path', 'path', kwargs)
        builder = ExternalLinkBuilder(path, file_path)
        self.set_link(name, builder)
        return builder

    @docval({'name':'name', 'type': str, 'doc': 'the name of this link'},
            {'name':'builder', 'type': 'LinkBuilder', 'doc': 'the LinkBuilder that represents this link'})
    def set_link(self, **kwargs):
        """
        Add a link to this group
        """
        name, builder = getargs('name', 'builder', kwargs)
        self.__set_builder(name, builder, GroupBuilder.__link)

    @docval({'name':'name', 'type': str, 'doc': 'the name of the attribute'},
            {'name':'value', 'type': None, 'doc': 'the attribute value'})
    def set_attribute(self, **kwargs):
        """
        Set an attribute for this group.
        """
        name, value = getargs('name', 'value', kwargs)
        super().__getitem__(GroupBuilder.__attribute)[name] = value
        self.obj_type[name] = GroupBuilder.__attribute

    #TODO: write unittests for this method
    def deep_update(self, builder):
        """ recursively update groups"""
        # merge subgroups
        groups = super(GroupBuilder, builder).__getitem__(GroupBuilder.__group)
        self_groups = super().__getitem__(GroupBuilder.__group)
        for name, subgroup in groups.items():
            if name in self_groups:
                self_groups[name].deep_update(subgroup)
            else:
                self.set_group(name, subgroup)
        # merge datasets
        datasets = super(GroupBuilder, builder).__getitem__(GroupBuilder.__dataset)
        self_datasets = super().__getitem__(GroupBuilder.__dataset)
        for name, dataset in datasets.items():
            #self.add_dataset(name, dataset)
            if name in self_datasets:
                self_datasets[name].deep_update(dataset)
                #super().__getitem__(GroupBuilder.__dataset)[name] = dataset
            else:
                #self.add_dataset(name, dataset.data, attributes=copy.copy(dataset.attributes)) #TODO: figure out if we want to do this copying, rather than just pointing to the argument
                self.set_dataset(name, dataset)
        # merge attributes
        for name, value in super(GroupBuilder, builder).__getitem__(GroupBuilder.__attribute).items():
            self.set_attribute(name, value)
        # merge links
        for name, link in super(GroupBuilder, builder).__getitem__(GroupBuilder.__link).items():
            self.set_link(name, link)

    def is_empty(self):
        """Returns true if there are no datasets, attributes, links or
           subgroups that contain datasets, attributes or links. False otherwise.
        """
        if (len(super().__getitem__(GroupBuilder.__dataset)) or
            len(super().__getitem__(GroupBuilder.__attribute)) or
            len(super().__getitem__(GroupBuilder.__link))):
            return False
        elif len(super().__getitem__(GroupBuilder.__group)):
            return all(g.is_empty() for g in super().__getitem__(GroupBuilder.__group).values())
        else:
            return True

    def __getitem__(self, key):
        """Like dict.__getitem__, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            raise KeyError(key)

    def get(self, key, default=None):
        """Like dict.get, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            return default

    def __get_rec(self, key_ar):
        # recursive helper for __getitem__
        if len(key_ar) == 1:
            return super().__getitem__(self.obj_type[key_ar[0]])[key_ar[0]]
        else:
            if key_ar[0] in super().__getitem__(GroupBuilder.__group):
                return super().__getitem__(GroupBuilder.__group)[key_ar[0]].__get_rec(key_ar[1:])
        raise KeyError(key_ar[0])


    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

    def __contains__(self, item):
        return self.obj_type.__contains__(item)

    def items(self):
        """Like dict.items, but iterates over key-value pairs in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).items(),
                                super().__getitem__(GroupBuilder.__dataset).items(),
                                super().__getitem__(GroupBuilder.__attribute).items(),
                                super().__getitem__(GroupBuilder.__link).items())

    def keys(self):
        """Like dict.keys, but iterates over keys in groups, datasets,
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).keys(),
                                super().__getitem__(GroupBuilder.__dataset).keys(),
                                super().__getitem__(GroupBuilder.__attribute).keys(),
                                super().__getitem__(GroupBuilder.__link).keys())

    def values(self):
        """Like dict.values, but iterates over values in groups, datasets,
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__(GroupBuilder.__group).values(),
                                super().__getitem__(GroupBuilder.__dataset).values(),
                                super().__getitem__(GroupBuilder.__attribute).values(),
                                super().__getitem__(GroupBuilder.__link).values())

class LinkBuilder(dict):
    def __init__(self, path, hard=False):
        super().__init__()
        self['path'] = path
        self['hard'] = hard

    @property
    def hard(self):
        return self['hard']

    @property
    def path(self):
        return self['path']


class ExternalLinkBuilder(LinkBuilder):
    def __init__(self, path, file_path):
        super().__init__(path, hard=False)
        self['file_path'] = file_path

    @property
    def file_path(self):
        return self['file_path']

class DatasetBuilder(dict):
    @docval({'name':'data', 'type': None, 'doc': 'a dictionary of datasets to create in this dataset', 'default': None},
            {'name':'dtype', 'type': (type, np.dtype), 'doc': 'the datatype of this dataset', 'default': None},
            {'name':'attributes', 'type': dict, 'doc': 'a dictionary of attributes to create in this dataset', 'default': dict()},
            {'name':'maxshape', 'type': (int, tuple), 'doc': 'the shape of this dataset. Use None for scalars', 'default': None},
            {'name':'chunks', 'type': bool, 'doc': 'whether or not to chunk this dataset', 'default': False})
    def __init__(self, **kwargs):
        '''
        Create a Builder object for a dataset
        '''
        super(DatasetBuilder, self).__init__()
        data, dtype, attributes, maxshape, chunks = getargs('data', 'dtype', 'attributes', 'maxshape', 'chunks', kwargs)
        self['data'] = data
        self['attributes'] = _copy.deepcopy(attributes)
        self.chunks = chunks
        self.maxshape = maxshape
        self.dtype = dtype

    @property
    def data(self):
        '''The data stored in the dataset represented by this builder'''
        return self['data']

    #@data.setter
    #def data(self, val):
    #    self['data'] = val

    @property
    def attributes(self):
        '''The attributes on the dataset represented by this builder'''
        return self['attributes']

    @docval({'name':'name', 'type': str, 'doc': 'the name of the attribute'},
            {'name':'value', 'type': None, 'doc': 'the attribute value'})
    def set_attribute(self, **kwargs):
        name, value = getargs('name', 'value', kwargs)
        self['attributes'][name] = value

    @docval({'name':'func', 'type': Callable, 'doc': 'the name of the attribute'})
    def add_iter_inspector(self, **kwargs):
        '''Add a function to call on each element in the dataset, as it is written to disk.'''
        func = getargs('func', kwargs)
        self._inspector = func

    @docval({'name':'dataset', 'type': 'DatasetBuilder', 'doc': 'the DatasetBuilder to merge into this DatasetBuilder'})
    def deep_update(self, **kwargs):
        """Merge data and attributes from given DatasetBuilder into this DatasetBuilder"""
        dataset = getargs('dataset', kwargs)
        if dataset.data:
            self['data'] = dataset.data #TODO: figure out if we want to add a check for overwrite
        self['attributes'].update(dataset.attributes)

    # XXX: leave this here for now, we might want it later
    #def __setitem__(self, args, val):
    #    raise NotImplementedError('__setitem__')
