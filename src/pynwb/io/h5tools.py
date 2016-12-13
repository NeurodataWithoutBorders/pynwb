__all__ = [
    'GroupBuilder',
    'DatasetBuilder',
    'LinkBuilder',
]

import itertools as _itertools
import posixpath as _posixpath
import copy as _copy

SOFT_LINK = 0
HARD_LINK = 1
EXTERNAL_LINK = 2

def set_attributes(obj, attributes):
    for key, value in attributes.iteritems():
        obj.attrs[key] = value

def write_group(parent, name, subgroups, datasets, attributes, links):
    group = parent.create_group(name)
    links_to_create = _copy.deepcopy(links)
    if subgroups:
        for subgroup_name, subgroup_builder in subgroups.iteritems():
            # do not create an empty group without attributes or links
            if subgroup_builder.is_empty():
                continue
            tmp_links = write_group(group,
                            subgroup_name,
                            subgroup_builder.groups,
                            subgroup_builder.datasets,
                            subgroup_builder.attributes,
                            subgroup_builder.links)
            for link_name, target in tmp_links.items():
                if link_name[0] != '/':
                    link_name = _posixpath.join(name, link_name)
                links_to_create[link_name] = target
    if datasets:
        for dset_name, dset_spec in datasets.iteritems():
            write_dataset(group,
                          dset_name,
                          dset_spec.get('data'),
                          dset_spec.get('attributes'))

    set_attributes(group, attributes)
    return links_to_create

def __get_shape__(data):
    shape = list()
    if hasattr(data, '__len__'):
        shape.append(len(data))
        shape.extend(__get_shape__(data[0]))
    return tuple(shape)

def __get_type__(data):
    if not hasattr(data, '__len__'):
        return type(data)
    else:
        return __get_type__(data[0])

def write_dataset(parent, name, data, attributes, function=None):
    if hasattr(data, '__len__'):
        __list_fill__(parent, name, data)
    else:
        chunk_size = 100
        #TODO: do something to figure out appropriate chunk_size
        __iter_fill__(parent, name, data, chunk_size, function=None)
    set_attributes(dest, attributes)
    
def __extend_dataset__(dset):
    new_shape = list(dset.shape)
    new_shape[0] = 2*new_shape[0]
    dset.resize(new_shape)

def __trim_dataset__(dset, length):
    new_shape = list(dset.shape)
    new_shape[0] = length
    dset.resize(new_shape)

def __iter_fill__(parent, name, data, chunk_size, function=None):
    #data_shape = list(__get_shape__(data))
    #data_shape[0] = None
    #data_shape = tuple(data_shape)
    data_iter = iter(data)
    curr_chunk = [next(data_iter) for i in range(chunk_size)]

    data_shape = __get_shape__(curr_chunk)
    data_dtype = __get_type__(curr_chunk)
    max_shape = list(data_shape)
    max_shape[0] = None
    dset = parent.require_dataset(name, shape=data_shape, dtype=data_dtype, maxshape=max_shape)

    idx = 0
    more_data = True
    args = [data_iter] * chunk_size
    chunks = _itertools.zip_longest(*args, fillvalue=None)

    if function:
        def proc_chunk(chunk):
            dset[idx:idx+len(chunk),] = chunk
            function(chunk)
    else:
        def proc_chunk(chunk):
            dset[idx:idx+len(chunk),] = chunk
            
    while more_data:
        try:
            next_chunk = next(chunks)
        except StopIteration:
            curr_chunk = list(filter(lambda x: x, curr_chunk))
            more_data = False
        if idx >= dset.shape[0] or idx+len(curr_chunk) > dset.shape[0]:
            __extend_dataset__(dset)
        #dset[idx:idx+len(curr_chunk),] = curr_chunk
        proc_chunk(curr_chunk)
        curr_chunk = next_chunk
        idx += chunk_size
    return dset

def __list_fill__(parent, name, data):
    data_shape = __get_shape__(data)
    data_dtype = __get_type__(data)
    dset = parent.require_dataset(name, shape=data_shape, dtype=data_dtype)
    if len(data) > dset.shape[0]:
        new_shape = list(dset.shape)
        new_shape[0] = len(data)
        dset.resize(new_shape)
    dset[:] = data
    

class GroupBuilder(dict):
    __link = 'links'
    __group = 'groups'
    __dataset = 'datasets'
    __attribute = 'attributes'

    def __init__(self, groups=dict(), datasets=dict(), attributes=dict(), links=dict()):
        """Create a GroupBuilder object
            Arguments:
                *groups* (string)      a dictionary of subgroups to create in this group
                *datasets* (string)      a dictionary of datasets to create in this group
                *attributes* (string)      a dictionary of attributes to assign to this group
                *links* (string)      a dictionary of links to create in this group
        """
        super().__init__()
        super().__setitem__(GroupBuilder.__group, groups)
        super().__setitem__(GroupBuilder.__dataset, datasets)
        super().__setitem__(GroupBuilder.__attribute, attributes)
        super().__setitem__(GroupBuilder.__link, links)
        self.obj_type = dict()
        for key in groups.keys():
            self.obj_type[key] = GroupBuilder.__group
        for key in datasets.keys():
            self.obj_type[key] = GroupBuilder.__dataset
        for key in attributes.keys():
            self.obj_type[key] = GroupBuilder.__attribute
        for key in links.keys():
            self.obj_type[key] = GroupBuilder.__link

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

    def add_dataset(self, name, data=None, attributes=dict()):
        """Add a dataset to this group
            Returns:
                the DatasetBuilder object for the dataset
        """
        #if name in self.obj_type:
        #    obj_type = self.obj_type[name]
        #    if obj_type != GroupBuilder.__dataset:
        #        raise KeyError("'%s' already exists as %s" % (name, obj_type))
        #    builder = super().__getitem__(GroupBuilder.__dataset)[name]
        #else:
        #if data:
        #    builder.data = data
        #if attributes:
        #    for k, v in attributes.items():
        #        builder.set_attribute(k, v)
        builder = DatasetBuilder(data, attribtues)
        super().__getitem__(GroupBuilder.__dataset)[name] = builder
        self.obj_type[name] = GroupBuilder.__dataset
        return builder
    
    def add_group(self, name, builder=None):
        """Add a subgroup to this group
            Returns:
                the GroupBuilder object for the subgroup
        """
        if name in self.obj_type:
            if obj_type != GroupBuilder.__group:
                raise KeyError("'%s' already exists as %s" % (name, obj_type))
        if not builder:
            tmp = GroupBuilder()
        else:
            tmp = builder
        super().__getitem__(GroupBuilder.__group)[name] = tmp
        self.obj_type[name] = GroupBuilder.__group
        return tmp

    def add_hard_link(self, name, path):
        """Add an hard link in this group.

            Arguments:
                *name* (string)      name of the link
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the hard link
        """
        super().__getitem__(GroupBuilder.__link)[name] = LinkBuilder(path, hard=True)
        self.obj_type[name] = GroupBuilder.__link
        return super().__getitem__(GroupBuilder.__link)[name]
    
    def add_soft_link(self, name, path):
        """Add an soft link in this group.

            Arguments:
                *name* (string)      name of the link
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the soft link
        """
        super().__getitem__(GroupBuilder.__link)[name] = LinkBuilder(path)
        self.obj_type[name] = GroupBuilder.__link
        return super().__getitem__(GroupBuilder.__link)[name]
    
    def add_external_link(self, name, file_path, path):
        """Add an external link in this group.

            Arguments:
                *name* (string)      name of the link
                *file_path* (string) path of the file that contains
                                     the object to link to
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the external link
        """
        super().__getitem__(GroupBuilder.__link)[name] = ExternalLinkBuilder(path, file_path)
        self.obj_type[name] = GroupBuilder.__link
        return super().__getitem__(GroupBuilder.__link)[name]
    
    def set_attribute(self, name, value):
        """Set an attribute for this group.
        """
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
                self_groups[name].update(subgroup)
            else:
                self.add_group(name, subgroup)
        # merge datasets
        datasets = super(GroupBuilder, builder).__getitem__(GroupBuilder.__dataset)
        self_datasets = super().__getitem__(GroupBuilder.__dataset)
        for name, dataset in datasets.items():
            if name in self_datasets:
                self_datasets[name].deep_update(dataset)
            else:
                #self.add_dataset(name, dataset.data, attributes=copy.copy(dataset.attributes)) #TODO: figure out if we want to do this copying, rather than just pointing to the argument
                self.add_dataset(name, dataset.data, attributes=dataset.attributes)
        # merge attributes
        for name, value in super(GroupBuilder, builder).__getitem__(GroupBuilder.__attribute).items():
            self.set_attribute(name, value)
        # merge links
        for name, link in super(GroupBuilder, builder).__getitem__(GroupBuilder.__link).items():
            super().__getitem__(GroupBuilder.__link)[name] = link
            self.obj_type[name] = GroupBuilder.__link

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
    def __init__(self, data=None, attributes=dict()):
        super(DatasetBuilder, self).__init__()
        self['data'] = data   
        self['attributes'] = dict()

    @property
    def data(self):
        return self['data']

    @data.setter
    def data(self, val):
        self['data'] = val

    @property
    def attributes(self):
        return self['attributes']

    def set_attribute(self, name, value):
        self['attributes'][name] = value

    def add_iter_inspector(self, callable_func):
        self._inspector = callable_func

    def deep_update(self, dataset):
        self['data'] = dataset.data #TODO: figure out if we want to add a check for overwrite
        self['attributes'].update(dataset.attributes)
    
    # XXX: leave this here for now, we might want it later
    #def __setitem__(self, args, val):
    #    raise NotImplementedError('__setitem__')
